# Alertas y umbrales iniciales

Los umbrales son hipótesis operativas de laboratorio. Se ajustarán con humo,
tráfico normal y estrés; no constituyen por sí solos un SLA medido.

| Alerta | Métrica, condición y duración | Severidad | Componente | Impacto o riesgo | Responsable y acción | Fundamento inicial |
|---|---|---|---|---|---|---|
| `Fixture2030ApiDown` | `up{job="fixture2030-api"} == 0` durante 30 s | crítica | API | ningún flujo HTTP queda accesible | Plataforma: revisar contenedor, logs y red; recuperar solo la API | seis scrapes fallidos evitan alertar por un arranque o demora aislada |
| `Fixture2030ApiHighErrorRate` | proporción HTTP 5xx sin `/health` mayor a 5 % durante 2 min | advertencia | API | la API responde pero falla un flujo funcional | Backend: identificar ruta y correlacionar dependencias | 5 % es experimental y debe recalibrarse con tráfico normal |
| `Fixture2030OutboxBacklog` | `fixture2030_outbox_pending{consumer="redis"} > 100` durante 5 min | advertencia | integración | demora de convergencia hacia Redis | Integración: revisar consumidor y reintentos sin eliminar mensajes | 100 es un umbral inicial de laboratorio |
| `Fixture2030OutboxWorkerDown` | `up{job="fixture2030-outbox"} == 0` durante 30 s | crítica | integración | las proyecciones dejan de avanzar, sin perder el hecho oficial | Recuperar el worker y observar convergencia | duración alineada con las fallas controladas locales |
| `Fixture2030OutboxDelayed` | mensaje pendiente más antiguo > 30 s durante 1 min | advertencia | integración | se incumple el objetivo local de propagación | revisar Redis, leases y reintentos | objetivo académico; no es SLA contractual |
| `Fixture2030OutboxFailed` | al menos un mensaje `FALLIDO` durante 1 min | advertencia | integración | se agotaron los reintentos automáticos | diagnosticar, corregir y reencolar manualmente | nunca se elimina silenciosamente |
| `Fixture2030MongoDown` | `fixture2030_dependency_up{dependency="mongodb"} == 0` durante 30 s | crítica | MongoDB | no se pueden confirmar eventos oficiales | Plataforma: revisar PRIMARY, réplica, volumen y conectividad | la API puede seguir viva; se necesita distinguir base caída de proceso caído |
| `Fixture2030RedisDown` | `redis_up{job="fixture2030-redis"} == 0` durante 30 s | crítica | Redis | sesiones no disponibles y caché en bypass | Plataforma: revisar contenedor, volumen y conectividad | separa la degradación temporal de la caída de la API |
| `Fixture2030RedisHighMemory` | memoria usada / `maxmemory` mayor a 85 % durante 5 min | advertencia | Redis | `allkeys-lfu` puede expulsar sesiones o caché antes del TTL | Plataforma: revisar TTL, cardinalidad y capacidad | deja margen antes del límite de 256 MB; se validará bajo estrés |
| `Fixture2030RedisEvictions` | al menos una eviction en 5 min durante 1 min | advertencia | Redis | presión de memoria o política inadecuada | Backend: correlacionar hit rate, memoria y escenario | en la línea base no se esperan evicciones |
| `Fixture2030CassandraDown` | `fixture2030_dependency_up{dependency="cassandra"} == 0` durante 30 s | crítica | Cassandra | comentarios no disponibles; fixture y sesiones continúan | Plataforma: revisar nodo, volumen y conectividad; no confirmar comentarios | demuestra degradación aislada del módulo social |
| `Fixture2030InfluxDown` | `fixture2030_dependency_up{dependency="influxdb"} == 0` durante 30 s | crítica | InfluxDB | posiciones, estadísticas y mapas no disponibles; núcleo oficial continúa | Plataforma: revisar nodo, token, volumen y red; recuperar solo InfluxDB | demuestra degradación aislada de telemetría |
| `Fixture2030TelemetryWriteErrors` | más de 5 errores de escritura en 5 min durante 1 min | advertencia | API/InfluxDB | lotes rechazados o referencias inconsistentes | Backend: revisar contrato, tipos, tags y disponibilidad | umbral inicial pendiente de carga normal |
| `Fixture2030Neo4jDown` | `fixture2030_dependency_up{dependency="neo4j"} == 0` durante 30 s | crítica | Neo4j | recorridos y recomendaciones no disponibles; núcleo oficial continúa | Plataforma: revisar nodo, secreto, volumen y red; recuperar solo Neo4j | demuestra degradación aislada del grafo |
| `Fixture2030GraphErrors` | más de 5 errores de grafo en 5 min durante 1 min | advertencia | API/Neo4j | patrones o recomendaciones fallan repetidamente | Backend: revisar consultas, cardinalidad y disponibilidad | umbral inicial pendiente de tráfico normal |
| `Fixture2030DataMartDown` | `fixture2030_dependency_up{dependency="datamart"} == 0` durante 30 s | advertencia | PostgreSQL | analítica y ETL degradados; núcleo continúa | Datos: revisar contenedor, secreto, volumen y red | aísla la analítica del camino oficial |
| `Fixture2030DataMartErrors` | más de 3 errores en 5 min durante 1 min | advertencia | API/Data Mart | cargas o consultas fallan repetidamente | Datos: revisar fuentes, SQL, frescura y capacidad | umbral experimental pendiente de carga normal |

Las fallas controladas de API, MongoDB, Redis, Cassandra, InfluxDB, Neo4j y Data Mart conservan valores
antes/durante/después y el estado `firing` cuando la regla correspondiente lo
permite. La alerta de memoria se ejercitará con carga. Outbox será validable
cuando exista el consumidor de proyecciones.
