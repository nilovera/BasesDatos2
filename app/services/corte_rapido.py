"""Corte rápido por dependencia (circuit breaker simple) - Hito 13.

Problema medido en la prueba controlada del Hito 13 (Redis detenido 120 s):
en Windows, conectarse a un puerto local cerrado tarda ~2 s en fallar (la pila TCP
reintenta antes de aceptar el rechazo). Cada solicitud de sesión ocupaba un hilo
de la API durante ~2,4 s solo para terminar en 503, y el throughput TOTAL cayó de
~133 a ~47 req/s aunque las otras cinco bases funcionaban.

Solución: cuando una base falla por indisponibilidad o timeout, durante
``ventana_segundos`` las solicitudes siguientes a ESA base responden 503 al
instante, sin intentar conectarse ("circuito abierto"). Pasada la ventana, la
siguiente solicitud vuelve a probar ("semiabierto"): si funciona, el circuito se
cierra; si no, se abre otra ventana. Mientras esa única prueba está en curso, las
demás siguen rechazadas (v2: en la v1 todas las solicitudes que llegaban al vencer la
ventana intentaban conectarse a la vez). El chequeo de /health/dependencias (cada
15 s) también cierra el circuito apenas el ping responde.

- No cambia el contrato HTTP: sigue siendo 503 DEPENDENCIA_NO_DISPONIBLE.
- No toca datos ni consultas: solo evita intentos que se sabe que van a fallar.
- ``ventana_segundos = 0`` desactiva el mecanismo (comportamiento anterior).
- Costo: tras la recuperación de la base, la API puede tardar hasta una ventana
  en volver a usarla (o menos, si antes corre el chequeo de salud).
"""

from __future__ import annotations

import threading
import time
from typing import Any

from prometheus_client import Counter

from app.exceptions import (
    DependencyTimeoutError,
    DependencyUnavailableError,
)


RECHAZOS = Counter(
    "fixture_corte_rapido_rechazos_total",
    "Solicitudes respondidas con 503 inmediato porque el circuito de la base estaba abierto.",
    ["dependencia"],
)
APERTURAS = Counter(
    "fixture_corte_rapido_aperturas_total",
    "Veces que se abrió el circuito de una base tras una falla de conexión o timeout.",
    ["dependencia"],
)

FALLAS_QUE_ABREN = (DependencyUnavailableError, DependencyTimeoutError)
METODOS_SIN_CORTE = {"close", "ping"}


class CorteRapido:
    def __init__(self, ventana_segundos: float) -> None:
        self.ventana = max(0.0, float(ventana_segundos))
        self._abierto_hasta: dict[str, float] = {}
        self._lock = threading.Lock()

    @property
    def activo(self) -> bool:
        return self.ventana > 0

    def abierto(self, dependencia: str) -> bool:
        return time.monotonic() < self._abierto_hasta.get(dependencia, 0.0)

    def estado(self) -> dict[str, bool]:
        return {dep: self.abierto(dep) for dep in self._abierto_hasta}

    def antes_de_llamar(self, dependencia: str) -> None:
        if not self.activo or not self._abierto_hasta.get(dependencia):
            return                                    # circuito cerrado: camino rápido, sin lock
        with self._lock:
            hasta = self._abierto_hasta.get(dependencia, 0.0)
            if not hasta:
                return
            ahora = time.monotonic()
            if ahora < hasta:
                RECHAZOS.labels(dependencia).inc()
                raise DependencyUnavailableError(dependencia)
            # Semiabierto: la ventana venció. ESTA solicitud es la única prueba; se vuelve a
            # armar la ventana para que las demás sigan rechazadas mientras la prueba dura
            # (v1 dejaba pasar a todas y cada una esperaba ~2,4 s: P95 de Redis 1,6 s).
            self._abierto_hasta[dependencia] = ahora + self.ventana

    def registrar_falla(self, dependencia: str) -> None:
        if not self.activo:
            return
        with self._lock:
            if not self.abierto(dependencia):
                APERTURAS.labels(dependencia).inc()
            self._abierto_hasta[dependencia] = time.monotonic() + self.ventana

    def registrar_exito(self, dependencia: str) -> None:
        if self._abierto_hasta.get(dependencia):
            with self._lock:
                self._abierto_hasta[dependencia] = 0.0


class AdaptadorProtegido:
    """Envuelve un adaptador: cada método público pasa por el corte rápido.

    ``ping`` no se corta (el diagnóstico siempre debe probar la base de verdad),
    pero su resultado sí actualiza el estado: un ping exitoso cierra el circuito.
    """

    def __init__(self, adaptador: Any, dependencia: str, corte: CorteRapido) -> None:
        self._adaptador = adaptador
        self._dependencia = dependencia
        self._corte = corte

    def __getattr__(self, nombre: str) -> Any:
        atributo = getattr(self._adaptador, nombre)
        if not callable(atributo) or nombre.startswith("_") or nombre == "close":
            return atributo

        dependencia, corte = self._dependencia, self._corte

        def llamada(*args: Any, **kwargs: Any) -> Any:
            if nombre not in METODOS_SIN_CORTE:
                corte.antes_de_llamar(dependencia)
            try:
                resultado = atributo(*args, **kwargs)
            except FALLAS_QUE_ABREN:
                corte.registrar_falla(dependencia)
                raise
            corte.registrar_exito(dependencia)
            return resultado

        return llamada
