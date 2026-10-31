"""Hito 13: el middleware de métricas cuenta por plantilla de ruta y base."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.middleware.metrics import PrometheusMiddleware


def _valor(nombre: str, **etiquetas: str) -> float:
    return REGISTRY.get_sample_value(nombre, etiquetas) or 0.0


def _app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)

    @app.get("/prueba/{codigo}")
    def prueba(codigo: str, request: Request):
        request.state.dependency = "MongoDB"
        if codigo == "caido":
            raise HTTPException(status_code=503)
        return {"codigo": codigo}

    @app.get("/metrics")
    def metrics():
        return {}

    return app


def test_cuenta_por_plantilla_codigo_y_dependencia():
    cliente = TestClient(_app())
    base_ok = _valor(
        "fixture_http_requests_total",
        metodo="GET", ruta="/prueba/{codigo}", codigo="200", dependencia="MongoDB",
    )
    base_503 = _valor(
        "fixture_http_requests_total",
        metodo="GET", ruta="/prueba/{codigo}", codigo="503", dependencia="MongoDB",
    )

    cliente.get("/prueba/EQ-01")
    cliente.get("/prueba/EQ-02")
    cliente.get("/prueba/caido")

    assert _valor(
        "fixture_http_requests_total",
        metodo="GET", ruta="/prueba/{codigo}", codigo="200", dependencia="MongoDB",
    ) == base_ok + 2
    assert _valor(
        "fixture_http_requests_total",
        metodo="GET", ruta="/prueba/{codigo}", codigo="503", dependencia="MongoDB",
    ) == base_503 + 1
    assert _valor(
        "fixture_http_request_duration_seconds_count",
        metodo="GET", ruta="/prueba/{codigo}", dependencia="MongoDB",
    ) >= 3


def test_no_se_cuenta_el_scraping():
    cliente = TestClient(_app())
    cliente.get("/metrics")
    assert _valor(
        "fixture_http_requests_total",
        metodo="GET", ruta="/metrics", codigo="200", dependencia="api",
    ) == 0.0
