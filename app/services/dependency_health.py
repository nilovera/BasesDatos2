"""Diagnóstico por dependencia para liveness / readiness (Hito 11).

Decisiones:

- No se consulta ninguna base en cada request normal. Los endpoints de
  negocio no invocan este módulo.
- El chequeo profundo ejecuta el ``ping()`` de cada adaptador en paralelo,
  cada uno con un límite de espera propio (``HEALTH_CHECK_TIMEOUT``).
- El resultado se guarda en caché durante ``CACHE_TTL_SECONDS``. Pedir
  ``/health/ready`` muchas veces seguidas no multiplica la carga sobre los
  motores.
- Un refresco forzado (``refrescar=true``) se limita a uno cada
  ``MIN_REFRESH_SECONDS`` para evitar que el diagnóstico se convierta en
  una fuente de carga.
- Ningún mensaje de driver se devuelve al cliente: solo la clasificación.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from app.exceptions import (
    DependencyMisconfiguredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


logger = logging.getLogger("fixture2030.health")


CACHE_TTL_SECONDS = 15.0
MIN_REFRESH_SECONDS = 5.0
HEALTH_CHECK_TIMEOUT = 3.0


@dataclass
class DependencyStatus:
    dependencia: str
    estado: str  # up | down | unknown | not_configured
    clasificacion: str
    detalle: str
    duracion_ms: float
    verificado_en: str


class DependencyHealthChecker:
    def __init__(
        self,
        checks: dict[str, Callable[[], str] | None],
        timeout_seconds: float = HEALTH_CHECK_TIMEOUT,
        cache_ttl_seconds: float = CACHE_TTL_SECONDS,
    ) -> None:
        self._checks = checks
        self._timeout = timeout_seconds
        self._cache_ttl = cache_ttl_seconds
        self._lock = threading.Lock()
        self._last_run = 0.0
        self._last_result: list[DependencyStatus] | None = None
        # Hilos daemon: un driver bloqueado no impide apagar la API.
        self._executor = ThreadPoolExecutor(
            max_workers=max(1, len(checks)),
            thread_name_prefix="health",
        )

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    def snapshot(self, refresh: bool = False) -> dict[str, Any]:
        with self._lock:
            now = time.monotonic()
            age = now - self._last_run

            must_run = (
                self._last_result is None
                or age >= self._cache_ttl
                or (refresh and age >= MIN_REFRESH_SECONDS)
            )

            if must_run:
                self._last_result = self._run_all()
                self._last_run = time.monotonic()
                age = 0.0

            result = self._last_result

        return {
            "dependencias": [asdict(item) for item in result],
            "desde_cache": not must_run,
            "antiguedad_segundos": round(age, 2),
            "ttl_cache_segundos": self._cache_ttl,
            "timeout_por_dependencia_segundos": self._timeout,
        }

    def _run_all(self) -> list[DependencyStatus]:
        futures = {}
        started = {}

        for name, check in self._checks.items():
            if check is None:
                continue
            started[name] = time.perf_counter()
            futures[name] = self._executor.submit(check)

        results: list[DependencyStatus] = []

        for name, check in self._checks.items():
            verified_at = datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            )

            if check is None:
                results.append(
                    DependencyStatus(
                        dependencia=name,
                        estado="not_configured",
                        clasificacion="sin_adaptador",
                        detalle="El módulo no está preparado en este entorno.",
                        duracion_ms=0.0,
                        verificado_en=verified_at,
                    )
                )
                continue

            future = futures[name]

            try:
                detail = future.result(timeout=self._timeout)
                estado, clasificacion = "up", "ok"
            except FutureTimeout:
                # El hilo puede seguir corriendo; se informa y no se espera.
                estado, clasificacion = "down", "timeout_diagnostico"
                detail = (
                    "Sin respuesta dentro del límite del chequeo "
                    f"({self._timeout:.1f} s)."
                )
            except DependencyTimeoutError:
                estado, clasificacion = "down", "timeout"
                detail = "La dependencia excedió su tiempo de espera."
            except DependencyMisconfiguredError as error:
                capa = (error.details or {}).get("capa", "configuracion")
                estado, clasificacion = "down", f"rechazo_{capa}"
                detail = (error.details or {}).get(
                    "descripcion",
                    error.message,
                )
            except DependencyUnavailableError:
                estado, clasificacion = "down", "no_disponible"
                detail = "No se pudo establecer la conexión."
            except Exception as error:  # noqa: BLE001
                estado, clasificacion = "unknown", "error_inesperado"
                detail = f"Error no clasificado: {type(error).__name__}."

            duration_ms = round(
                (time.perf_counter() - started[name]) * 1000,
                2,
            )

            status = DependencyStatus(
                dependencia=name,
                estado=estado,
                clasificacion=clasificacion,
                detalle=detail,
                duracion_ms=duration_ms,
                verificado_en=verified_at,
            )
            results.append(status)

            logger.info(
                json.dumps(
                    {
                        "evento": "dependency_check",
                        "dependencia": name,
                        "estado": estado,
                        "clasificacion": clasificacion,
                        "duracion_ms": duration_ms,
                    },
                    ensure_ascii=False,
                )
            )

        return results


def readiness_from(dependencias: list[dict[str, Any]]) -> tuple[str, int]:
    """Deriva el estado de readiness y su status HTTP.

    - ready (200): todas las dependencias configuradas están up.
    - degraded (200): al menos una up y al menos una down/unknown. La API
      sigue sirviendo las rutas de los motores disponibles (aislamiento
      por adaptador), por eso no se la retira del tráfico.
    - not_ready (503): ninguna dependencia configurada está up.
    """
    configured = [
        item for item in dependencias
        if item["estado"] != "not_configured"
    ]
    up = [item for item in configured if item["estado"] == "up"]

    if configured and len(up) == len(configured):
        return "ready", 200

    if up:
        return "degraded", 200

    return "not_ready", 503
