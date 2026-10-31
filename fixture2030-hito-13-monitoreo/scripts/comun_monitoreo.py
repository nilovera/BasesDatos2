"""Utilidades compartidas de los scripts del Hito 13.

- Rutas del hito y de la API.
- Lectura del .env de la API SIN imprimir valores (solo se usan para generar
  los archivos locales de .secretos/ y .env del monitoreo, que no se versionan).
- Consultas a la API HTTP de Prometheus y anotaciones en Grafana.

Se ejecuta con el Python del .venv de la API (ya tiene httpx y matplotlib).
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

HITO_DIR = Path(__file__).resolve().parents[1]
API_ROOT = HITO_DIR.parent
EVIDENCIA_DIR = HITO_DIR / "evidencia"
RESULTADOS_DIR = EVIDENCIA_DIR / "resultados_sin_secretos"
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

PROMETHEUS = "http://localhost:9090"
GRAFANA = "http://localhost:3000"
API = "http://127.0.0.1:8000"

# Contenedor de cada base (mismos nombres en los compose de los hitos 4-9 y en entorno-local/).
CONTENEDORES = {
    "mongodb": ("fixture2030-mongodb", "MongoDB"),
    "neo4j": ("fixture2030-neo4j", "Neo4j"),
    "cassandra": ("fixture2030-cassandra", "Cassandra"),
    "redis": ("fixture2030-redis", "Redis"),
    "influxdb": ("fixture2030-influxdb", "InfluxDB"),
    "iris": ("fixture2030-iris", "InterSystems IRIS"),
}

# Jobs que deben estar UP para considerar el monitoreo completo (cadvisor es opcional).
JOBS_ESPERADOS = [
    "prometheus", "fixture-api", "mongodb", "redis", "iris", "influxdb",
    "node-exporter", "sonda-tcp", "sonda-http",
]


def ahora() -> datetime:
    return datetime.now(TZ)


def ahora_iso() -> str:
    return ahora().isoformat(timespec="seconds")


def sello() -> str:
    return ahora().strftime("%Y%m%d-%H%M%S")


def escribir_json(ruta: Path, datos: Any) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def leer_env(ruta: Path) -> dict[str, str]:
    """Lee un .env simple (CLAVE='valor'). No imprime nada."""
    valores: dict[str, str] = {}
    if not ruta.exists():
        return valores
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "'\"":
            valor = valor[1:-1]
        valores[clave.strip()] = valor
    return valores


def commit_actual() -> str:
    try:
        salida = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, cwd=API_ROOT,
        )
        commit = salida.stdout.strip() or "desconocido"
        sucio = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10, cwd=API_ROOT,
        ).stdout.strip()
        return f"{commit}{' (con cambios sin commitear)' if sucio else ''}"
    except Exception:  # noqa: BLE001
        return "desconocido"


# ------------------------------------------------------------------ Prometheus
def prom_query(expr: str, momento: float | None = None) -> list[dict]:
    params = {"query": expr}
    if momento is not None:
        params["time"] = f"{momento:.3f}"
    r = httpx.get(f"{PROMETHEUS}/api/v1/query", params=params, timeout=20)
    r.raise_for_status()
    return r.json()["data"]["result"]


def prom_rango(expr: str, inicio: float, fin: float, paso: str = "5s") -> list[dict]:
    r = httpx.get(
        f"{PROMETHEUS}/api/v1/query_range",
        params={"query": expr, "start": f"{inicio:.3f}", "end": f"{fin:.3f}", "step": paso},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]["result"]


def prom_disponible() -> bool:
    try:
        return httpx.get(f"{PROMETHEUS}/-/ready", timeout=5).status_code == 200
    except httpx.HTTPError:
        return False


# --------------------------------------------------------------------- Grafana
def anotar_grafana(texto: str, tags: list[str], momento_ms: int | None = None) -> bool:
    """Crea una anotación en Grafana (marca vertical en todos los paneles).

    Usa la contraseña de admin del .env del monitoreo. Si falla no interrumpe la prueba.
    """
    env = leer_env(HITO_DIR / ".env")
    password = env.get("GRAFANA_ADMIN_PASSWORD")
    if not password:
        return False
    cuerpo = {"text": texto, "tags": ["prueba-controlada", *tags]}
    if momento_ms is not None:
        cuerpo["time"] = momento_ms
    try:
        r = httpx.post(f"{GRAFANA}/api/annotations", json=cuerpo, auth=("admin", password), timeout=5)
        return r.status_code == 200
    except httpx.HTTPError:
        return False
