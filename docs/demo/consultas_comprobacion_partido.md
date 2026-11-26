# Fixture 2030 — Consultas para comprobar el partido

Esta guía acompaña la transmisión web y permite explicar qué guarda cada base durante un partido. Las consultas se ejecutan fuera del front. No son resultados ya medidos: el contenido en crudo y su hora se obtienen al ejecutarlas en tu entorno.

## Elegir el partido y registrar la hora

El ejemplo usa `PAR-1004`, ya validado con semilla 2030 y resultado 1–2. Para una demo nueva, reemplazar ese ID por el que muestra la pantalla o `iniciar_demo_partido.ps1`.

Desde CMD, en `C:\BasesDatos2-trabajo-final`:

```cmd
powershell -NoProfile -Command "[DateTime]::UtcNow.ToString('o')"
docker compose exec -T mongo mongosh --quiet "mongodb://localhost:27017/fixture2030?directConnection=true" --eval "db.simulaciones.find({partidoId:'PAR-1004'}, {_id:0,simulacionId:1,partidoId:1,semilla:1,estado:1,segundoPartido:1,actualizadoEn:1}).forEach(printjson)"
```

Para guardar una sesión con las consultas y respuestas, abrir PowerShell y ejecutar `Start-Transcript -Path evidencia\comprobacion-partido.txt`; al terminar, ejecutar `Stop-Transcript`. Revisar el contenido antes de versionarlo. No imprimir credenciales ni variables de entorno completas.

## MongoDB — Fuente oficial

En una transacción se confirma el evento, se actualiza el partido y se agrega su mensaje Outbox. El front lee solamente eventos confirmados, sin exponer el plan futuro de la semilla.

```cmd
docker compose exec -T mongo mongosh --quiet "mongodb://localhost:27017/fixture2030?directConnection=true" --eval "printjson(db.partidos.findOne({_id:'PAR-1004'}, {_id:0,partidoId:1,estado:1,marcador:1,ultimaSecuencia:1,version:1,actualizadoEn:1})); db.eventos_oficiales.find({partidoId:'PAR-1004'}, {_id:0,eventoId:1,tipo:1,secuencia:1,ocurridoEn:1,datos:1}).sort({secuencia:1}).forEach(printjson)"
```

Qué observar: inicio, goles con autor y asistencia, tarjetas, sustituciones, VAR y final; el VAR no incrementa el marcador. `ocurridoEn` es el tiempo lógico del evento; no debe confundirse con la hora real de captura.

## Redis — Marcador proyectado

Outbox publica el marcador derivado y el worker de simulación actualiza el reloj. La vista usa el marcador Redis si su secuencia coincide con la oficial; durante una demora utiliza el documento oficial para evitar retroceder un gol.

```cmd
docker compose exec -T redis redis-cli --raw HGETALL marcador:partido:PAR-1004
docker compose exec -T redis redis-cli --raw XLEN eventos:partido:PAR-1004
```

El Hash contiene `local`, `visitante`, `estado`, `ultimaSecuencia`, `segundoPartido`, `minuto`, `velocidad` y `simulacionEstado`. El Stream registra los eventos publicados. Ambos son proyecciones de los eventos oficiales.

## Cassandra — Comentarios en vivo

Los comentarios se consultan por partido, bucket de minuto UTC y shard. Para obtener un bucket de la ejecución, leer `actualizadoEn` de la simulación en MongoDB y convertirlo a `yyyyMMddHHmm`. El front reúne los últimos tres buckets y oculta comentarios moderados.

Dentro de `cqlsh`, reemplazar `202611262001` por un bucket de la demo:

```sql
SELECT match_id, bucket, shard, created_at, comment_id,
       user_id, content, status
FROM fixture2030_comments.comments_by_match_bucket_shard
WHERE match_id = 'PAR-1004'
  AND bucket = '202611262001' AND shard = 0
LIMIT 30;
```

Repetir con `shard = 1`, `2` y `3`. No usar `ALLOW FILTERING`. Un resultado vacío puede significar que no hubo comentarios en esa partición; no demuestra una caída.

Para abrir la consola:

```cmd
docker compose exec cassandra cqlsh
```

Qué observar: comentarios diferentes, usuarios, hora real y estado `VISIBLE`. `comment_write_requests` guarda la clave idempotente mediante `IF NOT EXISTS`; un timeout recuperable se reintenta con la misma clave.

## InfluxDB — Posiciones y pelota

Ejecutar este bloque dentro de PowerShell. Lee el secreto local sin imprimir su valor:

```powershell
$token = (Get-Content '.secretos\influxdb-admin-token.txt' -Raw).Trim()
$headers = @{ Authorization = "Bearer $token" }
$sql = "SELECT jugador_id,equipo_id,x,y,segundo_partido,time FROM posiciones_jugador WHERE partido_id='PAR-1004' ORDER BY time DESC LIMIT 22"
$body = @{ db='fixture2030-detalle'; q=$sql; format='json' } | ConvertTo-Json
[DateTime]::UtcNow.ToString('o')
Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:8181/api/v3/query_sql' -Headers $headers -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 8
```

Para la pelota, reemplazar `$sql` y volver a construir y enviar `$body`:

```sql
SELECT x,y,segundo_partido,equipo_posesion_id,evento_id,time
FROM posiciones_pelota
WHERE partido_id='PAR-1004'
ORDER BY time DESC LIMIT 10
```

Para comprobar la ubicación de un gol, obtener `ocurridoEn` y sus coordenadas desde MongoDB y consultar ese timestamp exacto en la columna `time` de ambas tablas (filtrando también `jugador_id` para el goleador). No multiplicar el minuto visible por 60: el minuto se redondea hacia abajo y pierde los segundos. Los goles del plan están alineados con muestras de cinco segundos; la pelota y el goleador deben coincidir con la ubicación prevista.

El mapa de calor del equipo se calcula con esta consulta, limitada a una grilla de 240 celdas y sin truncar la historia a las primeras muestras:

```sql
SELECT LEAST(19,CAST(FLOOR(x/5) AS BIGINT)) AS cx,
       LEAST(11,CAST(FLOOR(y/(100.0/12)) AS BIGINT)) AS cy,
       COUNT(*) AS muestras
FROM posiciones_jugador
WHERE partido_id='PAR-1004' AND equipo_id='EQ-01'
GROUP BY cx,cy LIMIT 240
```

Para un jugador, reemplazar el filtro de equipo por `jugador_id='JUG-0001'`. La intensidad indica cantidad relativa de muestras, no velocidad ni probabilidad de gol. Las coordenadas están normalizadas de 0 a 100.

## Neo4j — Relaciones deportivas

Ejecutar en Neo4j Browser, usando las credenciales locales preparadas para la plataforma. Las relaciones llegan por Outbox y pueden aparecer unos instantes después de MongoDB.

```cypher
MATCH (j:Jugador)-[r:ANOTO|ASISTIO]->(p:Partido {id:'PAR-1004'})
RETURN j.id, j.nombre, type(r) AS relacion, r.eventoId, p.id;
```

```cypher
MATCH (ev:EventoOficial)-[:OCURRIO_EN]->(p:Partido {id:'PAR-1004'})
MATCH (entra:Jugador)-[r:ENTRO_POR]->(sale:Jugador)
WHERE r.eventoId = ev.id
RETURN ev.minuto, entra.nombre AS entra, sale.nombre AS sale, r.eventoId;
```

Qué observar: el mismo `eventoId` que MongoDB y una sola relación por evento al repetir su proyección. Las relaciones de `TUVO_GOL_ANULADO` describen el VAR, sin contarlo como `ANOTO`.

## Outbox — Comprobar convergencia

```cmd
powershell -ExecutionPolicy Bypass -File scripts\verificar_outbox.ps1
docker compose exec -T mongo mongosh --quiet "mongodb://localhost:27017/fixture2030?directConnection=true" --eval "db.outbox.find({partidoId:'PAR-1004'}, {_id:0,eventoId:1,estado:1,intentos:1}).sort({secuencia:1}).forEach(printjson)"
```

Al terminar y converger, los mensajes del partido deben quedar publicados y la verificación debe informar cero pendientes y cero fallidos. El total deduplicado es global; no representa solamente los eventos del último partido.

## Data Mart — Consulta analítica posterior

El Data Mart se refresca mediante ETL explícita; no se actualiza automáticamente por ver la transmisión. Para incorporar el nuevo partido y después consultar PostgreSQL:

```cmd
powershell -NoProfile -Command "Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:8000/api/v1/analitica/datamart/refrescar' -TimeoutSec 120 | ConvertTo-Json"
docker compose exec -T datamart psql -U fixture2030 -d fixture2030_analytics -c "SELECT p.partido_id,t.tipo,count(*) AS eventos,sum(f.goles) AS goles FROM analytics.fact_evento_partido f JOIN analytics.dim_partido p USING(partido_key) JOIN analytics.dim_tipo_evento t USING(tipo_evento_key) WHERE p.partido_id='PAR-1004' GROUP BY p.partido_id,t.tipo ORDER BY t.tipo;"
```

Los hechos de estadísticas de 15 minutos requieren que esos resúmenes existan previamente en InfluxDB; no deben asumirse por haber generado posiciones de jugadores y pelota.

## Evidencia a conservar

Registrar ID de simulación y partido, semilla, commit de código, hora UTC de las consultas y salidas reales. `probar_simulador_partido.ps1` verifica el flujo integral y guarda un resultado. `verificar_frontend.ps1` verifica HTML, recursos HTTP y lecturas de la transmisión. Una captura de pantalla documenta la presentación visual, pero no reemplaza las consultas ni los tests.
