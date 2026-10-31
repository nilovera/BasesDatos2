# Demostración controlada (estrategia de presentación, punto 6.3)

**Estrategia elegida:** presentación HTML para explicar + **Grafana** como pantalla principal de evidencia + **requests desde PowerShell o Postman** (una por base) + **un cliente nativo** si la FIFA pregunta por una estructura concreta. No se usa front: el foco son las bases (punto 6.4).

Todo se ejecuta desde la carpeta raíz de la API. Tiempo total de la demo en vivo: **~7 minutos** (bloques "Operación" y "Evidencia" del guion).

## 0. Preparación (antes de entrar, ~5 min)

```powershell
Set-Location C:\Users\corgn\Fixture2030\api
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\iniciar_monitoreo.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\verificar_targets.ps1   # todo UP
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\ejecutar_prueba_controlada.ps1 -Producto ninguno -Normal 120   # 2 min de tráfico para que Grafana tenga datos
```

Pestañas abiertas en el navegador: 1) `defensa/presentacion.html`, 2) Grafana `http://localhost:3000` (Last 15 minutes), 3) Prometheus `http://localhost:9090/alerts`, 4) Swagger `http://127.0.0.1:8000/docs`.

## 1. Un flujo completo: "consulta del partido en vivo" (6 bases, ~2 min)

Las mismas seis operaciones de la prueba de carga del Hito 12. Para cada una se dice **qué base responde y por qué esa estructura**:

```powershell
$api = "http://127.0.0.1:8000/api/v1"
Invoke-RestMethod "$api/equipos/EQ-01"                                                     # MongoDB: documento por _id
Invoke-RestMethod "$api/partidos/PAR-0001/eventos"                                         # Neo4j: recorrido partido -> equipos, sede, eventos
Invoke-RestMethod "$api/partidos/PAR-0001/comentarios?bucket_10min=203006131800&limit=5"   # Cassandra: UNA partición (partido, ventana de 10 min)
Invoke-RestMethod "$api/sesiones/SES-H12-0001"                                             # Redis: hash con TTL (ver ttl_segundos)
Invoke-RestMethod "$api/partidos/PAR-0001/estadisticas?desde=2030-06-13T20:00:00Z&hasta=2030-06-13T20:01:00Z&granularidad=detalle&equipo_id=ARG&limit=6"  # InfluxDB: ventana temporal
Invoke-RestMethod "$api/partidos/PAR-0001/detalle"                                         # IRIS: objeto Partido + Arbitro + EventoPartido
```

Alternativa: la colección de Postman de la API (`postman/`) o Swagger. Cada respuesta trae `fuente_datos` y el encabezado `X-Process-Time-Ms`.

**Punto a remarcar:** comentarios (Cassandra) y eventos (Neo4j) son ambos "cosas que pasan en un partido", pero se leen distinto. Los comentarios se piden como "los últimos N de una ventana", y la clave de partición ya los ordena. Los eventos se piden como relaciones con equipos y sede, y eso es un recorrido.

## 2. Falla controlada en vivo con Grafana (~4 min)

Versión corta de la prueba del hito: 30 s normales, Redis detenido 100 s, 40 s de recuperación.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\fixture2030-hito-13-monitoreo\scripts\ejecutar_prueba_controlada.ps1 -Normal 30 -Falla 100 -Recuperacion 40
```

Qué se muestra mientras corre (en este orden):

| Momento | Pantalla | Qué decir |
|---|---|---|
| `docker stop` | Grafana sección 1 | El puerto de Redis y "la API puede usar Redis" pasan a CAÍDA en 5-30 s. **Las otras 5 siguen en verde** |
| +30 s | Grafana sección 4 | Errores 5xx **solo** en Redis; "Circuito de corte rápido: ABIERTO" |
| +30 s | Grafana sección 2 | El throughput total **no cae** (con el corte rápido) |
| +80 s | Prometheus `/alerts` | `FixturePuertoDeBaseCerrado` y `FixtureBaseNoDisponibleParaLaApi` en *firing*, con impacto y acción |
| `docker start` | Grafana sección 1 | Redis vuelve a verde; las anotaciones naranjas marcan la falla |
| Al final | Consola | "Integridad DESPUÉS: 6 bases intactas" |

Si no hay tiempo para correrla: mostrar las capturas `evidencia/dashboards/02`, `03`, `04` y `07`, y `evidencia/comparacion_corte_rapido.png`.

## 3. Cliente nativo (solo si preguntan por una estructura, ~1 min)

Las contraseñas se ingresan cuando el cliente las pide (no se muestran en pantalla).

```powershell
docker exec -it fixture2030-cassandra cqlsh -e "SELECT creado_en, usuario_nombre FROM fixture2030_comentarios.comentarios_por_partido WHERE partido_id='PAR-0001' AND bucket_10min='203006131800' LIMIT 5;"
docker exec -it fixture2030-redis redis-cli HGETALL sesion:SES-H12-0001
docker exec -it fixture2030-redis redis-cli TTL sesion:SES-H12-0001
docker exec -it fixture2030-neo4j cypher-shell -u neo4j "MATCH (p:Partido {codigo:'PAR-0001'})-[r]-(x) RETURN type(r), labels(x), x.codigo LIMIT 10;"
docker exec -it fixture2030-mongodb mongosh -u admin --authenticationDatabase admin fixture2030 --eval "db.jugadores.find({equipo_id:'EQ-01'}).limit(3)"
```

## 4. Qué NO hacer en la defensa

- No ejecutar la prueba de carga completa del Hito 12 (6 minutos).
- No abrir los seis clientes nativos: solo el que responda a una pregunta.
- No mostrar `.env` ni `.secretos/`.

## 5. Plan B

Ver [`../docs/limitaciones_y_evidencia.md` §6](../docs/limitaciones_y_evidencia.md#6-plan-b-para-la-defensa-rnf7).
