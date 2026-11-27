# Estado de implementación y validación

Revisión documental: 27 de noviembre de 2026. Base de integración inspeccionada:
`f4cb9be15f996d2710b41c36b18b09eed7e07da2`, rama `trabajo-final`.

Este registro relaciona las afirmaciones del proyecto con el código y las
ejecuciones conservadas. Una prueba acredita el escenario, la versión y los
datos que utilizó; no certifica automáticamente modificaciones posteriores.
Las fechas de las carpetas de ejecución están expresadas en UTC.

## Plataforma integrada

| Componente | Resultado registrado | Evidencia |
|---|---|---|
| MongoDB | Replica set `rs0` con PRIMARY; 64 equipos, 1.024 jugadores, un partido, ocho eventos y cero jugadores huérfanos | [Verificación MongoDB](../evidencia/ejecuciones/20261126T002920Z/mongodb-verificacion.txt) |
| Redis | PONG, límite de 256 MB, `allkeys-lfu`, AOF activo y RDB operativo | [Verificación Redis](../evidencia/ejecuciones/20261126T002920Z/redis-verificacion.txt) |
| Cassandra | Nodo UN, tablas de comentarios y servicio disponible; RF=1 de laboratorio | [Verificación Cassandra](../evidencia/ejecuciones/20261126T002920Z/cassandra-verificacion.txt) |
| InfluxDB | Servicio, bases, tablas y acceso autenticado operativos | [Verificación InfluxDB](../evidencia/ejecuciones/20261126T002920Z/influxdb-verificacion.txt) |
| Neo4j | 64 equipos, 1.024 jugadores, un partido, seis confederaciones y 1.097 relaciones en el escenario base | [Verificación Neo4j](../evidencia/ejecuciones/20261126T002920Z/neo4j-verificacion.txt) |
| Data Mart | PostgreSQL, esquema estrella, consulta de salud y acceso desde la API operativos | [Verificación Data Mart](../evidencia/ejecuciones/20261126T002920Z/datamart-verificacion.txt) |
| Outbox | Worker disponible; cero pendientes y fallidos al capturar el escenario | [Verificación Outbox](../evidencia/ejecuciones/20261126T002920Z/outbox-verificacion.txt) |
| Plataforma | API, Prometheus y Grafana operativos junto con las dependencias | [Verificación integrada](../evidencia/ejecuciones/20261126T002920Z/plataforma-verificacion.txt) |

La captura integrada corresponde al commit
`854236118cab8eaff70755f55e7fc6c83ae8f7bf` y conserva
[metadatos](../evidencia/ejecuciones/20261126T002920Z/metadata.json).
Los conteos describen ese escenario base; aumentan al ejecutar nuevos partidos.
La retención de InfluxDB se define en la creación de las bases, no se deduce de
sus nombres ni de una comprobación de salud.

## Fallas controladas y convergencia

Se conservan pruebas de parada y recuperación de un contenedor con resultado
`OK`, cambio de disponibilidad `1 → 0 → 1` y activación de la alerta correspondiente.

| Servicio | Registro |
|---|---|
| API | [falla-api-20261124T024455Z](../evidencia/ejecuciones/falla-api-20261124T024455Z/resultado.json) |
| MongoDB | [falla-mongodb-20261124T025237Z](../evidencia/ejecuciones/falla-mongodb-20261124T025237Z/resultado.json) |
| Redis | [falla-redis-20261124T024737Z](../evidencia/ejecuciones/falla-redis-20261124T024737Z/resultado.json) |
| Cassandra | [falla-cassandra-20261124T025342Z](../evidencia/ejecuciones/falla-cassandra-20261124T025342Z/resultado.json) |
| InfluxDB | [falla-influxdb-20261124T195020Z](../evidencia/ejecuciones/falla-influxdb-20261124T195020Z/resultado.json) |
| Neo4j | [falla-neo4j-20261125T164936Z](../evidencia/ejecuciones/falla-neo4j-20261125T164936Z/resultado.json) |
| Data Mart | [falla-datamart-20261125T182335Z](../evidencia/ejecuciones/falla-datamart-20261125T182335Z/resultado.json) |

La [prueba de Outbox](../evidencia/ejecuciones/outbox-20261126T003830Z/resultado.json)
registró un evento pendiente durante la detención del worker, su publicación
posterior, dos intentos y una sola copia en el Stream Redis. Demuestra
recuperación e idempotencia para ese caso. La simulación integrada también
comprobó las relaciones deportivas de Neo4j.

Estas pruebas conservan los volúmenes. No equivalen a failover entre réplicas,
partición de red, recuperación de una región ni restauración desde backups.

## Rendimiento de lectura

Los perfiles siguientes usan el commit `3f7e4880a5a2d1f5af934be115340b73225543c6`.
La carga mezcla consultas de los subsistemas; no genera eventos ni comentarios.

| Perfil | Solicitudes | Errores | Throughput observado | p95 | p99 | Registro |
|---|---:|---:|---:|---:|---:|---|
| Humo corregido | 30 | 0 | 2,063 req/s | 48,234 ms | 52,833 ms | [231123Z](../evidencia/ejecuciones/carga-humo-20261125T231123Z/resultado.json) |
| Normal, tres repeticiones | 3.600 | 0 | 19,998 req/s | 34,926 ms | 46,605 ms | [231315Z](../evidencia/ejecuciones/carga-normal-20261125T231315Z/resultado.json) |
| Estrés | 4.800 | 0 | 79,932 req/s | 55,110 ms | 78,080 ms | [232053Z](../evidencia/ejecuciones/carga-estres-20261125T232053Z/resultado.json) |
| Humo de recuperación | 30 | 0 | 2,062 req/s | 38,819 ms | 45,311 ms | [232154Z](../evidencia/ejecuciones/carga-humo-20261125T232154Z/resultado.json) |

Las cuatro ejecuciones suman 8.460 solicitudes sin errores. Los perfiles de
humo y normal cumplieron sus SLO locales configurados: humo exige cero errores,
p95 ≤750 ms y p99 ≤1.500 ms; normal exige error ≤1 %, p95 ≤500 ms y p99 ≤1.000 ms. Estrés es informativo y se ejecutó con objetivo de 80 req/s;
el valor efectivamente alcanzado fue 79,932 req/s. No determina la capacidad máxima.

La [primera prueba diagnóstica](../evidencia/ejecuciones/carga-humo-20261125T230156Z/resultado.json)
tuvo 30 solicitudes sin errores, pero incumplió latencia, con p95 de 2.105,750 ms.
Se conserva separada para que la evaluación no omita un resultado desfavorable.
Los resultados incluyen muestras de recursos de contenedores; no acreditan
capacidad para millones de usuarios ni disponibilidad anual.

## Data Mart

| Medición | Fuente operacional p95 | Data Mart p95 | Resultado |
|---|---:|---:|---|
| [Sin pool, 182329Z](../evidencia/ejecuciones/rendimiento-datamart-20261125T182329Z/resultado.json) | 21,554 ms | 28,853 ms | Resultados equivalentes, cero errores; Data Mart más lento en este escenario |
| [Con pool, 192824Z](../evidencia/ejecuciones/rendimiento-datamart-20261125T192824Z/resultado.json) | 46,363 ms | 23,143 ms | Resultados equivalentes, cero errores; Data Mart más rápido en este escenario |

Cada ejecución realizó 100 consultas por alternativa sobre un partido. También
existen mediciones de ambos endpoints dentro de la carga mixta. La comparación
acredita los resultados de esas ejecuciones, sin aislar todos los factores que
cambiaron entre ellas ni demostrar ventajas generales a gran volumen.

## Simulador y front

La [prueba del simulador](../evidencia/ejecuciones/simulador-20261126T200113Z/resultado.json),
commit `d115007c5eb3eabc44d48cef85ce47f0dbe581d1`, finalizó `PAR-1004` con
semilla 2030, 5.400 segundos lógicos, marcador 1–2 y 17 eventos oficiales.
Verificó 156 comentarios, 20 muestras de posiciones de jugadores, 20 de pelota,
el marcador Redis, las relaciones Neo4j y la convergencia de Outbox. Las muestras
verificadas no equivalen a un conteo exhaustivo de toda la telemetría generada.

La [comprobación del front](../evidencia/ejecuciones/frontend-20261126T205119Z/resultado.json)
registró 22 posiciones, 103 celdas de mapa de calor de equipo, ocho de jugador
y 80 comentarios. Acredita las respuestas utilizadas por la interfaz; no es una
prueba visual automatizada de cada pantalla.

## Extensión de auditoría del incremento 15

La auditoría agrega código y esquemas a la base inspeccionada. Su validación
local comprende 170 pruebas unitarias y de regresión, incluidas 25 de auditoría,
con dobles de drivers. El paquete incluye sus resultados bajo
`evidencia/ejecuciones/auditoria-unitarias-*`.

El procedimiento `scripts/probar_auditoria.ps1` se ejecutó correctamente con
HTTP y motores reales del laboratorio Docker. El resultado se generó el
27 de noviembre de 2026 a las 04:05:31 UTC (01:05:31 de Argentina).

| Comprobación | Resultado observado |
|---|---|
| Publicación y replay | Un comentario lógico, sin duplicación |
| Historial de moderación | Publicación, ocultamiento y restauración: tres acciones |
| Replay de una moderación anterior | Conserva el estado visible posterior |
| Consultas y paginación | Historial por recurso y actor, con páginas de un registro |
| Identidad | Actor USR-0900 de sesión de laboratorio |
| Consulta sin sesión | Rechazo HTTP 403 |
| Entrega MongoDB → Cassandra | Creación de simulación registrada en el historial |

El [resultado original](../evidencia/ejecuciones/auditoria-20261127T040527Z/resultado.json)
conserva `estado: OK`, `duplicados: 0`, `consultaPublica: 403` y
`reenvioMongoCassandra: OK`. La transcripción de instalación confirma API 0.10.0
y servicios disponibles. La prueba preparó un cruce y no inició un partido.

Esta evidencia cubre esos recorridos, no todas las acciones auditables ni
fallas de replicación, capacidad o conservación de largo plazo. El JSON original
no incorpora el SHA de Git: se conserva sin alteraciones y se complementa con
un [registro de procedencia](../evidencia/ejecuciones/auditoria-20261127T040527Z/procedencia.json).
La revisión identificó HEAD `f4cb9be15f996d2710b41c36b18b09eed7e07da2` como base
del proyecto con los archivos del incremento 15 aplicados; ese SHA no identifica
por sí solo todo el contenido modificado que se ejecutó.

## Límites vigentes

- Servicios de un nodo y un único entorno local; sin alta disponibilidad real.
- Sesiones e identidades de laboratorio, sin autenticación de producción.
- Sin medición de RPO/RTO, failover regional o restauración integral desde backups.
- Sin benchmark representativo de escrituras masivas de comentarios o auditoría.
- Sin prueba concluyente de ventaja analítica a gran volumen.
- Sin acreditación de una defensa oral realizada ni de aprobación externa.

Los procedimientos ejecutables se mantienen disponibles para reproducir las
pruebas. Su existencia no se presenta como sustituto de un resultado registrado.
