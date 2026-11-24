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
| Redis | Redis Exporter y `/health` | disponibilidad, memoria, hits, misses, evictions, persistencia y conexiones | Directa |
| Cassandra | `/health`, métrica de dependencia y métricas de dominio | disponibilidad, comentarios y moderación | Funcional; JMX detallado pendiente |
| InfluxDB | pendiente | telemetria y mapas de calor | No incorporado |
| Neo4j | pendiente | relaciones y recorridos | No incorporado |

La solucion posee tres targets directos: API, Prometheus y Redis Exporter.
MongoDB y Cassandra se observan funcionalmente a través de la API; sus
exporters internos quedan pendientes.
