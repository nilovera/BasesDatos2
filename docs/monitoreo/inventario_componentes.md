# Inventario de monitoreo

El inventario distingue medición directa, exporter e inferencia funcional. Una
base pendiente o presente solamente en un diagrama no se declara monitoreada.

| Componente | Modelo y función en Fixture2030 | Puerto o endpoint | Mecanismo | Métricas seleccionadas | Riesgo observado | Limitación actual |
|---|---|---|---|---|---|---|
| API FastAPI | integración de los subsistemas y contrato HTTP | `8000`, `/health`, `/metrics` | instrumentación directa con `prometheus-client` | disponibilidad, requests, p95, 5xx, eventos, comentarios y Outbox | indisponibilidad, errores y aumento de latencia | un worker; todavía sin escenario de capacidad |
| MongoDB | documentos autoritativos de catálogo, partidos, eventos y Outbox | `27017`; salud funcional desde `/health` | inferencia de la API mediante `hello` y métrica `fixture2030_dependency_up` | PRIMARY disponible y pendientes de Outbox | no poder confirmar eventos oficiales o acumular propagaciones | un miembro; sin exporter ni alta disponibilidad real |
| Redis | clave-valor para Cache-Aside, sesiones, TTL, contadores y ranking | `6379`; exporter `9121` | Redis Exporter directo y salud funcional de la API | `redis_up`, memoria, hit/miss, evictions, persistencia y conexiones | pérdida anticipada de temporales, saturación o sesiones no disponibles | standalone; RDB/AOF no equivalen a replicación |
| Cassandra | wide-column para comentarios y vistas por consulta | `9042`; salud funcional desde `/health` | inferencia de la API y contadores de dominio | disponibilidad, publicaciones, replays, lecturas, moderaciones y errores | módulo social degradado, partición caliente o divergencia de vistas | RF=1 local; JMX, compactions y tombstones pendientes para RF=3 |
| InfluxDB | series de posiciones, estadísticas y resúmenes temporales | `8181`, `/health`, `/metrics` autenticados | target directo de Prometheus, salud funcional y contadores de API | disponibilidad, escrituras, consultas, errores y persistencia | telemetría degradada, pérdida de series o cardinalidad excesiva | un nodo; sin alta disponibilidad ni backup probado |
| Prometheus | series técnicas de observabilidad | `9090`, API HTTP de Prometheus | métricas propias y tres jobs configurados | estado de targets, evaluación de reglas y retención de 7 días | pérdida de visibilidad o reglas sin evaluar | una instancia; no es almacenamiento funcional del Fixture |
| Grafana | visualización de Prometheus | `3000`, `/api/health` | verificación operativa y provisioning versionado | salud del visualizador y dashboard exportable | defensa sin paneles o datasource no disponible | no es target de Prometheus; capturas finales pendientes |
| Neo4j | grafo de relaciones entre jugadores, equipos y partidos | pendiente | pendiente | pendiente | recorridos y relaciones no demostrados | no incorporado todavía |

Prometheus posee cuatro targets directos: Prometheus, API, Redis Exporter e InfluxDB. La
disponibilidad de MongoDB y Cassandra se mide funcionalmente desde la API. El
dashboard debe indicar esta diferencia para no presentar una inferencia como
métrica interna de la base.
