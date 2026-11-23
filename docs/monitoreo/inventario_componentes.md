# Inventario de monitoreo

Este inventario distingue lo que ya se observa de lo que se incorporara con
los siguientes motores. No implica que todos los componentes cumplan todavia
un SLA.

| Componente | Fuente actual | Estado observable | Estado de la cobertura |
|---|---|---|---|
| API FastAPI | `/metrics` y `/health` | disponibilidad, solicitudes, latencia, errores y resultado funcional | Directa |
| Prometheus | metricas propias | disponibilidad del recolector y evaluacion de reglas | Directa |
| MongoDB | `/health` y metricas de dominio de la API | PRIMARY, transaccion funcional y pendientes de Outbox | Indirecta; exporter pendiente |
| Grafana | `/api/health` y dashboard | salud del visualizador | Verificacion operativa; no es target de Prometheus |
| Redis | pendiente | sesiones, cache y concurrencia | No incorporado |
| Cassandra | pendiente | comentarios y moderacion | No incorporado |
| InfluxDB | pendiente | telemetria y mapas de calor | No incorporado |
| Neo4j | pendiente | relaciones y recorridos | No incorporado |

La exigencia de observar al menos tres componentes de la solucion se cerrara
cuando se incorpore Redis con su exporter. Hasta entonces hay dos targets
directos y MongoDB se observa solamente a traves de la API.
