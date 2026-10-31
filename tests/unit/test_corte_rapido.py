"""Hito 13: el corte rápido evita reintentar una base caída durante la ventana."""

import time

import pytest

from app.exceptions import DependencyUnavailableError
from app.services.corte_rapido import AdaptadorProtegido, CorteRapido


class AdaptadorFalso:
    def __init__(self):
        self.llamadas = 0
        self.caido = True

    def get_sesion(self, sesion_id):
        self.llamadas += 1
        if self.caido:
            time.sleep(0.05)              # simula la espera de una conexión rechazada
            raise DependencyUnavailableError("Redis")
        return {"sesion_id": sesion_id}

    def ping(self):
        if self.caido:
            raise DependencyUnavailableError("Redis")
        return "PONG"


def test_con_circuito_abierto_no_se_intenta_la_conexion():
    base = AdaptadorFalso()
    protegido = AdaptadorProtegido(base, "Redis", CorteRapido(ventana_segundos=10))
    with pytest.raises(DependencyUnavailableError):
        protegido.get_sesion("SES-1")            # primer intento real: abre el circuito
    inicio = time.perf_counter()
    for _ in range(20):
        with pytest.raises(DependencyUnavailableError):
            protegido.get_sesion("SES-1")
    assert base.llamadas == 1                     # los 20 siguientes no tocaron la base
    assert time.perf_counter() - inicio < 0.05    # y respondieron al instante


def test_un_ping_exitoso_cierra_el_circuito():
    base = AdaptadorFalso()
    corte = CorteRapido(ventana_segundos=10)
    protegido = AdaptadorProtegido(base, "Redis", corte)
    with pytest.raises(DependencyUnavailableError):
        protegido.get_sesion("SES-1")
    base.caido = False
    assert protegido.ping() == "PONG"             # el diagnóstico de salud prueba de verdad
    assert protegido.get_sesion("SES-1") == {"sesion_id": "SES-1"}


def test_ventana_cero_mantiene_el_comportamiento_anterior():
    base = AdaptadorFalso()
    protegido = AdaptadorProtegido(base, "Redis", CorteRapido(ventana_segundos=0))
    for _ in range(3):
        with pytest.raises(DependencyUnavailableError):
            protegido.get_sesion("SES-1")
    assert base.llamadas == 3


def test_al_vencer_la_ventana_solo_una_solicitud_prueba_la_base():
    base = AdaptadorFalso()
    corte = CorteRapido(ventana_segundos=0.2)
    protegido = AdaptadorProtegido(base, "Redis", corte)
    with pytest.raises(DependencyUnavailableError):
        protegido.get_sesion("SES-1")             # abre el circuito
    time.sleep(0.25)                               # vence la ventana
    corte.antes_de_llamar("Redis")                 # la primera pasa (es la prueba)...
    with pytest.raises(DependencyUnavailableError):
        corte.antes_de_llamar("Redis")             # ...y las siguientes siguen rechazadas
