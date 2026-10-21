"""Pruebas unitarias del diagnóstico por dependencia (Hito 11).

No requieren motores: los chequeos se reemplazan por funciones locales.
"""

import time

from app.exceptions import (
    DependencyMisconfiguredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)
from app.services.dependency_health import (
    DependencyHealthChecker,
    readiness_from,
)


def _ok():
    return "ok"


def _down():
    raise DependencyUnavailableError("X")


def _timeout():
    raise DependencyTimeoutError("X")


def _auth():
    raise DependencyMisconfiguredError("X", "autenticacion")


def _lento():
    time.sleep(2)
    return "tarde"


def _by_name(snapshot):
    return {item["dependencia"]: item for item in snapshot["dependencias"]}


def test_clasificacion_por_tipo_de_falla():
    checker = DependencyHealthChecker(
        checks={
            "A": _ok,
            "B": _down,
            "C": _timeout,
            "D": _auth,
            "E": None,
        },
        timeout_seconds=1,
    )
    try:
        items = _by_name(checker.snapshot())
    finally:
        checker.close()

    assert items["A"]["estado"] == "up"
    assert items["B"]["clasificacion"] == "no_disponible"
    assert items["C"]["clasificacion"] == "timeout"
    assert items["D"]["clasificacion"] == "rechazo_autenticacion"
    assert items["E"]["estado"] == "not_configured"


def test_timeout_del_diagnostico_no_bloquea():
    checker = DependencyHealthChecker(
        checks={"lento": _lento},
        timeout_seconds=0.2,
    )
    started = time.perf_counter()
    try:
        items = _by_name(checker.snapshot())
    finally:
        checker.close()

    assert time.perf_counter() - started < 1.5
    assert items["lento"]["clasificacion"] == "timeout_diagnostico"


def test_cache_evita_consultar_en_cada_request():
    calls = {"n": 0}

    def contar():
        calls["n"] += 1
        return "ok"

    checker = DependencyHealthChecker(
        checks={"A": contar},
        timeout_seconds=1,
        cache_ttl_seconds=60,
    )
    try:
        first = checker.snapshot()
        second = checker.snapshot()
        third = checker.snapshot(refresh=True)  # < 5 s: no refresca
    finally:
        checker.close()

    assert calls["n"] == 1
    assert first["desde_cache"] is False
    assert second["desde_cache"] is True
    assert third["desde_cache"] is True


def test_readiness():
    up = {"estado": "up"}
    down = {"estado": "down"}
    nc = {"estado": "not_configured"}

    assert readiness_from([up, up, nc]) == ("ready", 200)
    assert readiness_from([up, down]) == ("degraded", 200)
    assert readiness_from([down, down]) == ("not_ready", 503)
