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
