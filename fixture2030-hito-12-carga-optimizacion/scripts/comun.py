"""Utilidades compartidas del Hito 12 (rutas, configuración, huellas e info del entorno).

Ningún valor secreto se imprime ni se escribe en la evidencia: las credenciales se leen
del .env de la API (que no se versiona) a través de app.config.settings.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

HITO_DIR = Path(__file__).resolve().parents[1]
API_ROOT = HITO_DIR.parent
CONFIG_DIR = HITO_DIR / "config"
DATOS_DIR = HITO_DIR / "datos-o-generadores"
EVIDENCIA_DIR = HITO_DIR / "docs" / "evidencia"
CATALOGO_PATH = DATOS_DIR / "catalogo_claves.json"
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

# Prefijos de los datos sintéticos que crea este hito (y que limpia limpiar_datos_de_prueba.py).
PREFIJO_PARTIDO_IRIS = "PAR-H12"
PREFIJO_SESION_REDIS = "SES-H12-"

# Campos que cambian entre lecturas sin que el dato esté mal (se excluyen de la huella).
CAMPOS_VOLATILES = {"ttl_segundos"}

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


def ahora_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def cargar_config(ruta: str | None = None) -> dict[str, Any]:
    """Lee config/configuracion.json si existe; si no, la de ejemplo (versionada)."""
    candidatos = [Path(ruta)] if ruta else [
        CONFIG_DIR / "configuracion.json",
        CONFIG_DIR / "configuracion-ejemplo.json",
    ]
    for candidato in candidatos:
        if candidato.exists():
            data = json.loads(candidato.read_text(encoding="utf-8"))
            data["_archivo"] = str(candidato.relative_to(HITO_DIR)) if candidato.is_relative_to(HITO_DIR) else str(candidato)
            return data
    raise FileNotFoundError("No se encontró ningún archivo de configuración en config/.")


def get_settings():
    """Settings de la API (lee el .env local). Importado tarde para no exigirlo en todos los scripts."""
    from app.config.settings import get_settings as _gs  # noqa: WPS433
    return _gs()


def _limpiar(valor: Any) -> Any:
    if isinstance(valor, dict):
        return {k: _limpiar(v) for k, v in sorted(valor.items()) if k not in CAMPOS_VOLATILES}
    if isinstance(valor, list):
        return [_limpiar(v) for v in valor]
    return valor


def huella(cuerpo: Any) -> str:
    """SHA-256 del JSON canónico de la respuesta, sin campos volátiles."""
    canonico = json.dumps(_limpiar(cuerpo), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()[:16]


def _cmd(args: list[str], timeout: float = 15) -> str:
    try:
        salida = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=API_ROOT)
        return salida.stdout.strip()
    except Exception as error:  # noqa: BLE001
        return f"no disponible ({type(error).__name__})"


def info_git() -> dict[str, Any]:
    estado = _cmd(["git", "status", "--porcelain", "--", "app"])
    return {
        "commit": _cmd(["git", "rev-parse", "--short", "HEAD"]),
        "rama": _cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "codigo_api_modificado_sin_commit": bool(estado and not estado.startswith("no disponible")),
        "archivos_api_modificados": estado.splitlines() if estado and not estado.startswith("no disponible") else [],
    }


def info_contenedores() -> list[dict[str, str]]:
    salida = _cmd(["docker", "ps", "--format", "{{.Names}}|{{.Image}}|{{.Status}}"])
    filas = []
    for linea in salida.splitlines():
        partes = linea.split("|")
        if len(partes) == 3 and "fixture2030" in partes[0]:
            filas.append({"nombre": partes[0], "imagen": partes[1], "estado": partes[2]})
    return filas


def info_versiones() -> dict[str, str]:
    paquetes = ["fastapi", "uvicorn", "starlette", "httpx", "pymongo", "neo4j", "cassandra-driver",
                "redis", "intersystems_irispython", "psutil", "matplotlib"]
    versiones = {"python": platform.python_version()}
    for paquete in paquetes:
        try:
            versiones[paquete] = metadata.version(paquete)
        except metadata.PackageNotFoundError:
            versiones[paquete] = "no instalado"
    return versiones


def info_hardware() -> dict[str, Any]:
    data: dict[str, Any] = {
        "sistema": f"{platform.system()} {platform.release()} ({platform.version()})",
        "procesador": platform.processor() or "no informado",
    }
    try:
        import psutil
        data["nucleos_fisicos"] = psutil.cpu_count(logical=False)
        data["procesadores_logicos"] = psutil.cpu_count(logical=True)
        data["ram_total_gb"] = round(psutil.virtual_memory().total / 1024 ** 3, 1)
    except ImportError:
        data["nota"] = "psutil no instalado: sin datos de CPU/RAM"
    return data


def info_config_api() -> dict[str, Any]:
    """Solo parámetros NO secretos de la configuración de la API."""
    try:
        s = get_settings()
    except Exception as error:  # noqa: BLE001
        return {"error": type(error).__name__}
    return {
        "dependency_timeout_seconds": s.dependency_timeout_seconds,
        "iris_pool_size": int(os.getenv("IRIS_POOL_SIZE", getattr(s, "iris_pool_size", 0) or 0)),
        "uvicorn_workers": 1,
        "nota": "credenciales omitidas a propósito",
    }


def escribir_json(ruta: Path, data: Any) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ comentarios sintéticos (Cassandra)
NOMBRES = ["Ana Torres", "Bruno Silva", "Carla Méndez", "Diego Rossi", "Elena García", "Francisco Costa",
           "Gabriela Ruiz", "Hugo Pereira", "Inés Romero", "Julián Sosa"]
FRASES = ["Qué partido", "Vamos que se puede", "Penal clarísimo", "Gran atajada", "Hay que cambiar el esquema",
          "El árbitro no cobra nada", "Golazo", "Se viene el empate", "Mucha presión arriba", "Partidazo"]


def comentarios_sinteticos(por_bucket: int, semilla: int):
    """Genera SIEMPRE los mismos comentarios (claves deterministas) para 96 partidos x 12 buckets.

    Sigue la misma regla de fechas del generador del Hito 6: 8 partidos por día, actividad de
    120 minutos desde las 18:00, buckets de 10 minutos. El UUID es uuid5 de un texto fijo, por lo
    que volver a cargar hace upsert (no duplica) y la limpieza puede recalcular las claves exactas.
    """
    import random
    import uuid
    from datetime import datetime, timedelta
    rng = random.Random(semilla + 6)
    espacio = uuid.UUID("12121212-2030-4000-8000-000000000012")
    for n in range(1, 97):
        partido = f"PAR-{n:04d}"
        dia = datetime(2030, 6, 13) + timedelta(days=(n - 1) // 8)
        for k in range(12):
            inicio = dia.replace(hour=18) + timedelta(minutes=10 * k)
            bucket = inicio.strftime("%Y%m%d%H%M")
            for j in range(por_bucket):
                creado = inicio + timedelta(seconds=rng.randint(0, 599), milliseconds=j)
                usuario_n = rng.randint(1, 5000)
                yield {
                    "partido_id": partido, "bucket_10min": bucket, "creado_en": creado,
                    "comentario_id": uuid.uuid5(espacio, f"H12|{partido}|{bucket}|{j}"),
                    "usuario_id": f"USR-{usuario_n:04d}", "usuario_nombre": rng.choice(NOMBRES),
                    "contenido": f"{rng.choice(FRASES)} (sintético H12)",
                    "estado_moderacion": "visible" if rng.random() > 0.1 else "pendiente",
                    "likes": rng.randint(0, 50), "bucket_dia": dia.strftime("%Y%m%d"),
                }


def sesion_cassandra():
    from cassandra.cluster import Cluster
    s = get_settings()
    cluster = Cluster(contact_points=s.cassandra_contact_points, port=s.cassandra_port, connect_timeout=10)
    return cluster, cluster.connect(s.cassandra_keyspace)
