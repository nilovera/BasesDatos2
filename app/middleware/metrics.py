"""Métricas de aplicación para Prometheus (Hito 13).

Qué se mide directamente en la API (capa de APLICACIÓN):

- ``fixture_http_requests_total``: contador de solicitudes por método, ruta
  (plantilla, no la URL concreta), código HTTP y base de datos que atiende
  la ruta (``dependencia``).
- ``fixture_http_request_duration_seconds``: histograma del tiempo que la API
  tarda en responder, con las mismas etiquetas salvo el código. Es el mismo
  tiempo que ya informa el encabezado ``X-Process-Time-Ms``.
- ``fixture_http_requests_in_progress``: solicitudes en curso (gauge).

Decisiones:

- Se usa la PLANTILLA de la ruta (``/api/v1/partidos/{codigo}/eventos``) y no
  la URL real, para que la cantidad de series no crezca con cada partido o
  sesión consultada (cardinalidad acotada).
- ``/metrics`` no se cuenta a sí mismo: el scraping de Prometheus cada 15 s
  ensuciaría el throughput de negocio.
- Es un middleware ASGI puro (sin ``BaseHTTPMiddleware``) para que el costo
  por solicitud sea mínimo: en el Hito 12 la API ya era intensiva en CPU.
- La instrumentación solo LEE el estado de la solicitud: no modifica
  respuestas ni datos de ninguna base (RNF5).
"""

from __future__ import annotations

import time

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    disable_created_metrics,
)
from starlette.types import ASGIApp, Message, Receive, Scope, Send


# Las series *_created no aportan al análisis y duplican la salida.
disable_created_metrics()

RUTAS_EXCLUIDAS = {"/metrics"}

# Buckets elegidos a partir del Hito 12: P50 de la mayoría de las rutas entre
# 5 y 30 ms, P95 global 120-135 ms con 80 usuarios, umbral de alerta 250 ms.
BUCKETS_SEGUNDOS = (
    0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0,
)

SOLICITUDES = Counter(
    "fixture_http_requests_total",
    "Solicitudes HTTP atendidas por la API del Fixture 2030.",
    ["metodo", "ruta", "codigo", "dependencia"],
)

DURACION = Histogram(
    "fixture_http_request_duration_seconds",
    "Tiempo de respuesta de la API (segundos), medido dentro del proceso.",
    ["metodo", "ruta", "dependencia"],
    buckets=BUCKETS_SEGUNDOS,
)

EN_CURSO = Gauge(
    "fixture_http_requests_in_progress",
    "Solicitudes HTTP que la API está procesando en este momento.",
)


def _plantilla_de_ruta(scope: Scope) -> str:
    route = scope.get("route")
    path = getattr(route, "path", None)
    return path if path else "sin_ruta"


def _dependencia(scope: Scope) -> str:
    # Las rutas guardan en request.state.dependency la base que consultan.
    # Starlette guarda request.state en scope["state"].
    state = scope.get("state") or {}
    valor = state.get("dependency") if isinstance(state, dict) else None
    return str(valor) if valor else "api"


class PrometheusMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http" or scope.get("path") in RUTAS_EXCLUIDAS:
            await self.app(scope, receive, send)
            return

        codigo = 500
        inicio = time.perf_counter()
        EN_CURSO.inc()

        async def send_con_codigo(message: Message) -> None:
            nonlocal codigo
            if message["type"] == "http.response.start":
                codigo = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_con_codigo)
        finally:
            duracion = time.perf_counter() - inicio
            EN_CURSO.dec()
            metodo = scope.get("method", "GET")
            ruta = _plantilla_de_ruta(scope)
            dependencia = _dependencia(scope)
            SOLICITUDES.labels(metodo, ruta, str(codigo), dependencia).inc()
            DURACION.labels(metodo, ruta, dependencia).observe(duracion)
