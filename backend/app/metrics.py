from prometheus_client import Counter, Gauge, Histogram


HTTP_REQUESTS = Counter(
    "fixture2030_http_requests",
    "Solicitudes HTTP recibidas por la API",
    ["method", "route", "status"],
)
HTTP_DURATION = Histogram(
    "fixture2030_http_request_duration_seconds",
    "Duración de solicitudes HTTP",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
EVENTS_CONFIRMED = Counter(
    "fixture2030_events_confirmed",
    "Eventos oficiales confirmados",
    ["type"],
)
IDEMPOTENCY_REPLAYS = Counter(
    "fixture2030_idempotency_replays",
    "Respuestas recuperadas por idempotencia",
)
OUTBOX_PENDING = Gauge(
    "fixture2030_outbox_pending",
    "Mensajes pendientes en la Outbox de MongoDB",
)
CACHE_READS = Counter(
    "fixture2030_cache_reads",
    "Lecturas Cache-Aside de partidos",
    ["result"],
)
CACHE_INVALIDATIONS = Counter(
    "fixture2030_cache_invalidations",
    "Invalidaciones de cache solicitadas despues de una escritura oficial",
    ["result"],
)
SESSION_OPERATIONS = Counter(
    "fixture2030_session_operations",
    "Operaciones sobre sesiones temporales de Redis",
    ["operation", "result"],
)
DEPENDENCY_UP = Gauge(
    "fixture2030_dependency_up",
    "Disponibilidad de dependencias observada por la API",
    ["dependency"],
)
COMMENT_OPERATIONS = Counter(
    "fixture2030_comment_operations",
    "Operaciones de comentarios en Cassandra",
    ["operation", "result"],
)
TELEMETRY_OPERATIONS = Counter(
    "fixture2030_telemetry_operations",
    "Operaciones de series temporales en InfluxDB",
    ["operation", "result"],
)
GRAPH_OPERATIONS = Counter(
    "fixture2030_graph_operations",
    "Operaciones de recorridos y recomendaciones en Neo4j",
    ["operation", "result"],
)
