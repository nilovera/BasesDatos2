# Inventario de monitoreo

El inventario distingue instrumentación directa, exporter, collector nativo y
comprobación funcional. Una consulta de salud no se presenta como una colección
completa de métricas internas.

| Componente | Función | Endpoint o puerto | Mecanismo y métricas | Límite |
|---|---|---|---|---|
| API FastAPI | Contratos y coordinación | 8000; /health y /metrics | Requests, histograma de latencia, errores y contadores de dominio | Instancia local sin HA |
| Worker Outbox | Redis y Neo4j | 9101 interno; /metrics | Salud, profundidad, edad, reintentos y fallidos | Un consumidor; etiqueta histórica consumer=redis |
| MongoDB | Catálogo y núcleo oficial | 27017 | Salud PRIMARY; collector API con serverStatus/dbStats: conexiones, operaciones, bytes de datos, almacenamiento e índices | Un miembro; no exporter independiente ni redundancia |
| Redis | Caché, sesiones y temporales | 6379; exporter 9121 | Redis Exporter: salud, memoria, hit/miss, evictions, persistencia y conexiones | Standalone; RDB/AOF no equivale a réplica |
| Cassandra | Comentarios y auditoría | 9042 | Salud y operaciones funcionales de comentarios | RF=1; sin JMX completo ni métricas específicas de retraso del relay de auditoría |
| InfluxDB | Telemetría y ventanas | 8181 | Target directo autenticado; salud y operaciones de API | Core de un nodo; sin backup integral probado |
| Neo4j | Recorridos y proyección deportiva | 7474/7687 | Salud Bolt y contadores funcionales | Community de un nodo; sin métricas internas completas |
| Data Mart | ETL y consulta analítica | 5433 | Salud SQL y contadores de ETL/consulta | Sin exporter PostgreSQL; ETL batch y nodo único |
| Prometheus | Series técnicas y reglas | 9090 | Métricas propias, targets y evaluación de reglas | Una instancia; retención local de siete días |
| Grafana | Visualización | 3000; /api/health | Salud y provisioning del dashboard | No es un target directo; no hay captura visual de cada prueba |

Prometheus tiene cinco targets directos: él mismo, API, worker Outbox, Redis
Exporter e InfluxDB. El collector MongoDB se expone dentro del scrape de API,
no agrega otro target. La salud funcional de las dependencias también se
expone desde la API.

El dashboard vigente prioriza API y los cinco motores operacionales. Data Mart
y Outbox conservan métricas aunque no se muestren en todos sus paneles. La
revisión se fundamenta en configuración y código, junto con las ejecuciones
identificadas en [estado de validación](../estado_validacion.md).
