"""Endpoint /metrics para Prometheus (Hito 13).

Además de las métricas HTTP del middleware, en cada scraping se publican:

- ``fixture_dependencia_up{dependencia}``: 1 si el ping liviano del adaptador
  (el mismo de /health/dependencias del Hito 11) respondió, 0 si no. Mide la
  disponibilidad de cada base VISTA DESDE LA API (conexión + autenticación +
  operación mínima), que es más que "el puerto está abierto".
- ``fixture_dependencia_chequeo_segundos{dependencia}``: duración de ese ping.
- ``fixture_dependencia_desde_cache``: 1 si el diagnóstico salió de la caché
  de 15 s del Hito 11. El scraping no multiplica la carga sobre los motores.
- ``fixture_api_proceso_cpu_segundos_total`` y
  ``fixture_api_proceso_memoria_bytes``: consumo del proceso de la API
  (psutil). El colector estándar de prometheus_client solo funciona en Linux
  y la API corre en Windows.
- ``fixture_api_info``: versión y tamaño del pool de IRIS en uso (Hito 12).
"""

from __future__ import annotations

import os

from fastapi import APIRouter, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    generate_latest,
)
from prometheus_client.core import (
    CounterMetricFamily,
    GaugeMetricFamily,
    InfoMetricFamily,
)

from app.config.settings import get_settings

try:
    import psutil
except ImportError:  # sin psutil solo se omiten las métricas del proceso
    psutil = None


router = APIRouter(tags=["Sistema"])


class FixtureCollector:
    """Colector que se evalúa en cada scraping."""

    def __init__(self) -> None:
        self.health_checker = None
        self.corte_rapido = None
        self._proceso = psutil.Process(os.getpid()) if psutil else None

    def describe(self):
        return []

    def collect(self):
        settings = get_settings()

        info = InfoMetricFamily(
            "fixture_api",
            "Datos de la instancia de la API.",
        )
        info.add_metric(
            [],
            {
                "version": settings.app_version,
                "entorno": settings.app_env,
                "iris_pool_size": str(settings.iris_pool_size),
                "corte_rapido_segundos": str(settings.corte_rapido_segundos),
            },
        )
        yield info

        if self._proceso is not None:
            tiempos = self._proceso.cpu_times()
            cpu = CounterMetricFamily(
                "fixture_api_proceso_cpu_segundos",
                "Segundos de CPU consumidos por el proceso de la API.",
            )
            cpu.add_metric([], tiempos.user + tiempos.system)
            yield cpu

            memoria = GaugeMetricFamily(
                "fixture_api_proceso_memoria_bytes",
                "Memoria residente del proceso de la API.",
            )
            memoria.add_metric([], self._proceso.memory_info().rss)
            yield memoria

        if self.corte_rapido is not None and self.corte_rapido.activo:
            abierto = GaugeMetricFamily(
                "fixture_corte_rapido_abierto",
                "1 si el circuito de la base está abierto (503 inmediato).",
                labels=["dependencia"],
            )
            for dependencia, valor in self.corte_rapido.estado().items():
                abierto.add_metric([dependencia], 1.0 if valor else 0.0)
            yield abierto

        if self.health_checker is None:
            return

        snapshot = self.health_checker.snapshot()

        up = GaugeMetricFamily(
            "fixture_dependencia_up",
            "1 si la API puede usar la base (ping del adaptador), 0 si no.",
            labels=["dependencia"],
        )
        duracion = GaugeMetricFamily(
            "fixture_dependencia_chequeo_segundos",
            "Duración del último ping de la API a cada base.",
            labels=["dependencia"],
        )
        for item in snapshot["dependencias"]:
            if item["estado"] == "not_configured":
                continue
            up.add_metric(
                [item["dependencia"]],
                1.0 if item["estado"] == "up" else 0.0,
            )
            duracion.add_metric(
                [item["dependencia"]],
                item["duracion_ms"] / 1000,
            )
        yield up
        yield duracion

        cache = GaugeMetricFamily(
            "fixture_dependencia_desde_cache",
            "1 si el diagnóstico de dependencias se tomó de la caché de 15 s.",
        )
        cache.add_metric([], 1.0 if snapshot["desde_cache"] else 0.0)
        yield cache


COLECTOR = FixtureCollector()
REGISTRY.register(COLECTOR)


@router.get(
    "/metrics",
    include_in_schema=False,
    summary="Métricas en formato Prometheus",
)
def metrics(request: Request) -> Response:
    # Se enlaza en cada llamada por si la API se reinició (lifespan nuevo).
    COLECTOR.health_checker = getattr(
        request.app.state,
        "health_checker",
        None,
    )
    COLECTOR.corte_rapido = getattr(request.app.state, "corte_rapido", None)
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )
