# Fixture 2030 — trabajo final

Integración final del trabajo de Ingeniería de Datos II dentro del repositorio
`nilovera/BasesDatos2`, rama `trabajo-final`.

**Estado:** MongoDB autoritativo, API transaccional, worker Outbox, Redis para datos calientes,
Cassandra para comentarios, InfluxDB para series temporales, Neo4j para
relaciones, un Data Mart analítico en PostgreSQL y observabilidad con Prometheus y Grafana.

## Preparar la rama limpia

La rama `trabajo-final` debe comenzar sin heredar el contenido de `monitoreo` ni
de otra rama histórica. Las implementaciones anteriores se conservan como
antecedentes y se recuperan archivo por archivo después de su revisión.

Desde una copia limpia del repositorio:

```text
git clone https://github.com/nilovera/BasesDatos2.git
cd BasesDatos2
git switch --orphan trabajo-final
```

Copiar entonces el contenido de este paquete en la raíz del repositorio, revisar
`git status` y crear el primer commit. No realizar un merge completo de las ramas
anteriores.

## Verificar el commit inicial

Instalar Python 3.10 o superior. Desde CMD o PowerShell:

```text
python -m scripts.catalogo --check
python -m unittest discover -s tests -v
```

Si Windows utiliza el lanzador de Python, reemplazar `python` por `py`. Esta
primera entrega no requiere paquetes externos.

Para regenerar los JSON del catálogo:

```text
python -m scripts.catalogo
python -m scripts.catalogo --check
```

## Contenido y estado

| Carpeta | Contenido | Estado |
|---|---|---|
| `data/fuentes/` | Definición reproducible del dataset | Implementado |
| `data/catalogo/` | 64 equipos, 1.024 jugadores, equivalencias, partido de demostración y eventos iniciales vacíos | Generado y verificado |
| `scripts/` | Generación y comprobación de integridad | Implementado |
| `tests/` | Pruebas del catálogo, contratos, dominio, API e infraestructura | Ejecutadas estáticamente |
| `docs/antecedentes/` | Siete documentos de diseño previos | Conservados como antecedentes |
| `docs/diseno/` | Convenciones y decisiones de la rama final | Base inicial documentada |
| `backend/` | FastAPI, contrato OpenAPI, transacción, idempotencia y worker Outbox | Implementado con proyección idempotente a Redis |
| `mongodb/` | Replica set, validadores, índices, carga y verificación | Implementado y validado en Docker |
| `redis/` | Cache-Aside, sesiones, TTL, LFU, RDB y AOF | Implementado y validado en Docker; evidencia final pendiente |
| `cassandra/` | Esquema por consulta, buckets, shards e idempotencia | Implementado y validado en Docker; evidencia final pendiente |
| `influxdb/` | Retención, telemetría, cursores, mapas de calor y resúmenes | Implementado y validado |
| `neo4j/` | Proyección, restricciones, CRUD, recomendaciones y caminos | Implementado; ejecución Docker pendiente |
| `datamart/` | Esquema estrella, hechos de eventos y resúmenes de 15 minutos | Implementado; ejecución Docker pendiente |
| `infra/` | Prometheus, reglas de alerta, Grafana y dashboard inicial | Implementado y ejecutado en Docker |
| `evidencia/` | Resultados trazables por commit y prueba de falla controlada | Estructura y captura automatizadas; ejecuciones pendientes de versionar |

## Arquitectura objetivo

La solución final utiliza cinco motores operacionales y un destino analítico separado:

| Motor | Responsabilidad principal |
|---|---|
| MongoDB | Fuente oficial de equipos, jugadores, partidos, alineaciones y eventos deportivos |
| Cassandra | Comentarios, moderación y vistas por partido/usuario con buckets y shards |
| Redis | Sesiones, caché, concurrencia y datos temporales |
| InfluxDB | Estadísticas, posiciones y series temporales |
| Neo4j | Relaciones y recorridos entre jugadores, equipos y partidos |
| PostgreSQL Data Mart | Dimensiones conformadas, hechos y consultas analíticas sin cargar el camino operacional |

InterSystems IRIS fue evaluado y queda excluido de la arquitectura ejecutable.
La decisión, las alternativas consideradas, las responsabilidades reasignadas y
sus consecuencias están documentadas en
[`ADR-001`](docs/diseno/ADR-001-exclusion-iris.md).

## Decisiones iniciales

- La integración se construye en la rama limpia `trabajo-final`.
- Las ramas anteriores permanecen como evidencia; no se fusionan completas.
- Cada incorporación debe indicar origen, cambios, prueba y limitaciones.
- IDs internos: `EQ-01`, `JUG-0001`, `PAR-0001` y `EVE-000001`.
- `ARG -> EQ-01` y `MEX -> EQ-33` son las equivalencias explícitas de la demostración; las demás quedan pendientes de fuente validada.
- El partido Argentina-México del 13/06/2030 a las 20:00 UTC es un dato sintético de laboratorio.
- El partido comienza en `PROGRAMADO`, sin eventos oficiales.
- El catálogo de 96 partidos de la carga histórica de Neo4j es un antecedente, no el fixture final validado.
- `InfluxDB` es la rama de referencia; `InlfuxDB` está desactualizada y no se incorpora.

## Orden de trabajo

1. Conservar la validación de API, transacciones, idempotencia y los cinco motores, además de Prometheus y Grafana.
2. Ejecutar y conservar la evidencia reproducible del Data Mart en Docker.
3. Procesar la Outbox y actualizar las proyecciones idempotentes. **Implementado para Redis.**
4. Completar usuarios, asistencias y participación real de jugadores.
5. Agregar exporters, alertas y dashboards de los cinco motores.
6. Ejecutar humo, tráfico normal, estrés y recuperación.
7. Preparar la demostración y defensa final.

## Evidencia reproducible

Con la plataforma operativa, capturar el estado reproducible:

```text
powershell -ExecutionPolicy Bypass -File scripts\capturar_evidencia.ps1 -Scenario verificacion-integrada
```

La convergencia de la Outbox se valida deteniendo solo el consumidor, creando
un evento oficial y simulando un replay posterior a la publicación:

```text
powershell -ExecutionPolicy Bypass -File scripts\verificar_outbox.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_outbox.ps1
```

Luego ejecutar la falla controlada de la API. El script detiene solamente ese
contenedor, espera que Prometheus registre `up=0` y la alerta pase a `firing`,
y siempre intenta recuperarlo en un bloque `finally`:

```text
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_api.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_plataforma.ps1
```

Los resultados quedan bajo `evidencia/ejecuciones/`. Deben revisarse antes de
versionarlos y complementarse con capturas de Grafana de la misma ventana
temporal. Las consultas, umbrales, responsables y limitaciones están en
[`docs/monitoreo`](docs/monitoreo/).

La correspondencia entre la consigna de monitoreo, lo implementado y la
evidencia todavía pendiente está en la
[`matriz de cumplimiento`](docs/monitoreo/matriz_cumplimiento_hito_13.md).

La captura exige por defecto un commit limpio. Las fallas de MongoDB, Redis,
Cassandra, InfluxDB y Neo4j también generan `resultado.json` con commit, valores
antes/durante/después, alerta y recuperación:

```text
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_mongodb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_neo4j.ps1
```

## Accesos y detención segura

Con la plataforma iniciada:

- API y Swagger: `http://localhost:8000/docs`
- métricas de la API: `http://localhost:8000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- InfluxDB 3 Core: `http://localhost:8181` (API autenticada, no es una UI)
- Neo4j Browser: `http://localhost:7474`
- PostgreSQL Data Mart: `localhost:5433` (sin UI; consultas por API/psql)

Para detener sin borrar MongoDB, Redis, Cassandra, InfluxDB ni las series de monitoreo:

```text
powershell -ExecutionPolicy Bypass -File scripts\detener_plataforma.ps1
```

No utilizar `docker compose down -v` en las pruebas normales.

## Incremento 04 Redis

Redis implementa Cache-Aside, invalidación después de una escritura oficial,
sesiones con renovación explícita, contadores atómicos, ranking, evicción LFU,
snapshots RDB y AOF. Para probarlo:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_patrones_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_redis.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_redis.ps1
```

El modelo y sus trade-offs están en
[`06_3_modelo_fisico_redis.md`](docs/diseno/06_3_modelo_fisico_redis.md).

## Incremento 05 Cassandra

Cassandra conserva comentarios por partido y por usuario, aplica idempotencia,
moderación y paginación mediante cursor opaco `(timestamp, comentarioId)`, y se
degrada sin bloquear el fixture:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_comentarios_cassandra.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_cassandra.ps1
```

El modelo y la diferencia entre RF=1 local y RF=3 objetivo están en
[`06_4_modelo_fisico_cassandra.md`](docs/diseno/06_4_modelo_fisico_cassandra.md).

## Incremento 06 InfluxDB

InfluxDB conserva posiciones y estadísticas detalladas durante 7 días y
resúmenes de 15 minutos durante 365 días. La API valida referencias comunes,
escribe lotes completos, pagina por `(timestamp, jugadorId)` y reconstruye
mapas de calor:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_telemetria_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_influxdb.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_influxdb.ps1
```

El modelo, la seguridad del token, el cursor y las limitaciones de
participación están en
[`06_5_modelo_fisico_influxdb.md`](docs/diseno/06_5_modelo_fisico_influxdb.md).

## Incremento 07 Neo4j

Neo4j proyecta el catálogo común para resolver rivales, recomendaciones y
caminos de varios saltos. La carga usa `MERGE`, restricciones únicas y una
prueba CRUD temporal que no altera el catálogo:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_grafo_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_neo4j.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_neo4j.ps1
```

El modelo y sus límites están en
[`06_6_modelo_fisico_neo4j.md`](docs/diseno/06_6_modelo_fisico_neo4j.md).

## Incremento 08 Data Mart

PostgreSQL materializa un esquema estrella separado. El ETL por lote es
idempotente, conserva dos granos y permite comparar la misma consulta contra la
fuente operacional:

```text
powershell -ExecutionPolicy Bypass -File scripts\iniciar_plataforma.ps1
powershell -ExecutionPolicy Bypass -File scripts\verificar_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\comparar_rendimiento_datamart.ps1 -Iteraciones 100
powershell -ExecutionPolicy Bypass -File scripts\probar_persistencia_datamart.ps1
powershell -ExecutionPolicy Bypass -File scripts\probar_falla_datamart.ps1
```

El diseño y el protocolo honesto del Hito 12 están en
[`06_7_modelo_fisico_datamart.md`](docs/diseno/06_7_modelo_fisico_datamart.md) y
[`hito_12_datamart.md`](docs/rendimiento/hito_12_datamart.md).

## Incremento 09 — carga y SLO de laboratorio

El simulador recorre la cadena completa con perfiles reproducibles de humo,
tráfico normal y estrés. Conserva percentiles, throughput, errores y muestras
de CPU/memoria por contenedor sin modificar el partido oficial:

```text
powershell -ExecutionPolicy Bypass -File scripts\probar_carga.ps1 -Perfil humo
powershell -ExecutionPolicy Bypass -File scripts\probar_carga.ps1 -Perfil normal
powershell -ExecutionPolicy Bypass -File scripts\probar_carga.ps1 -Perfil estres
```

Los perfiles, SLI, SLO iniciales y limitaciones están en
[`pruebas_carga_sla_slo.md`](docs/rendimiento/pruebas_carga_sla_slo.md).

Ver el [plan de incorporación](docs/plan_incorporacion.md), el
[registro de los 17 puntos](docs/pendientes.md) y las
[fuentes inspeccionadas](docs/fuentes.md). Las tareas de usuarios, asistencias,
telemetría, simulación y carga están registradas en
[tareas posteriores a la integración](docs/tareas_integracion_final.md).

## Alcance de las verificaciones actuales

MongoDB fue ejecutado en el equipo del grupo con 64 equipos, 1.024 jugadores,
un partido, replica set PRIMARY e idempotencia de la carga. La API, Redis,
Cassandra, Prometheus y Grafana también fueron iniciados y verificados. Las
pruebas funcionales incluyen persistencia Redis, comentarios Cassandra y
degradación controlada de los servicios. Todavía deben versionarse las
ejecuciones finales y no existen mediciones de capacidad, SLO ni convergencia
completa.
