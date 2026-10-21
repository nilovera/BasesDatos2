"""Limpieza opcional del diagnóstico (Hito 11, RNF15).

Elimina **solo** lo que generan los propios scripts del Hito 11 y nunca
toca datos de dominio, contenedores ni volúmenes:

1. claves ``diag:hito11:*`` que hayan quedado en Redis (normalmente expiran
   solas a los 2 s; esto cubre el caso de una ejecución interrumpida);
2. logs de las instancias temporales de la API (``logs/api_falla_*.stderr.log``);
3. cachés ``__pycache__`` de la carpeta de scripts.

Además verifica que no haya quedado escuchando la API temporal del escenario
``config`` (puerto 8001 por defecto). Las evidencias de ``docs/evidencia`` no
se borran: son entregables.

Por defecto solo muestra qué limpiaría (simulación). Para ejecutar:
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\limpieza.py --confirmar
"""

from __future__ import annotations

import argparse
import shutil
import socket
import sys

from common import (
    REPO_ROOT,
    SCRIPTS_DIR,
    Config,
    Redactor,
    parse_overrides,
    preparar_consola,
)


PREFIJO_REDIS = "diag:hito11:*"


def limpiar_redis(cfg: Config, confirmar: bool) -> str:
    try:
        import redis
    except ImportError:
        return "SKIP  Redis: redis-py no instalado."

    cliente = redis.Redis(
        host=cfg.get("REDIS_HOST", "127.0.0.1"),
        port=cfg.get_int("REDIS_PORT", 6379),
        db=cfg.get_int("REDIS_DATABASE", 0),
        password=cfg.get("REDIS_PASSWORD"),
        socket_connect_timeout=cfg.timeout,
        socket_timeout=cfg.timeout,
        decode_responses=True,
    )
    try:
        claves = list(cliente.scan_iter(PREFIJO_REDIS, count=200))
        if not claves:
            return f"OK    Redis: no hay claves {PREFIJO_REDIS}."
        if not confirmar:
            return f"SIM   Redis: se eliminarían {len(claves)} claves {PREFIJO_REDIS}."
        borradas = cliente.delete(*claves)
        return f"OK    Redis: {borradas} claves {PREFIJO_REDIS} eliminadas (solo diagnóstico)."
    except Exception as error:  # noqa: BLE001
        return f"SKIP  Redis no disponible ({type(error).__name__}): no hay nada que limpiar allí ahora."
    finally:
        cliente.close()


def limpiar_archivos(confirmar: bool) -> list[str]:
    mensajes = []
    logs = sorted((REPO_ROOT / "logs").glob("api_falla_*.stderr.log"))
    caches = [p for p in SCRIPTS_DIR.rglob("__pycache__") if p.is_dir()]

    for ruta in logs:
        relativo = ruta.relative_to(REPO_ROOT)
        if confirmar:
            ruta.unlink(missing_ok=True)
            mensajes.append(f"OK    eliminado {relativo}")
        else:
            mensajes.append(f"SIM   se eliminaría {relativo}")

    for ruta in caches:
        relativo = ruta.relative_to(REPO_ROOT)
        if confirmar:
            shutil.rmtree(ruta, ignore_errors=True)
            mensajes.append(f"OK    eliminado {relativo}")
        else:
            mensajes.append(f"SIM   se eliminaría {relativo}")

    if not logs and not caches:
        mensajes.append("OK    no hay logs temporales ni cachés de los scripts.")
    return mensajes


def verificar_api_temporal(puerto: int) -> str:
    try:
        with socket.create_connection(("127.0.0.1", puerto), timeout=1):
            return (
                f"ADV   hay un proceso escuchando en 127.0.0.1:{puerto}. Si es la API temporal de "
                "falla_controlada, cerrarlo (no se detiene automáticamente para no cortar otro servicio)."
            )
    except OSError:
        return f"OK    no queda ninguna API temporal escuchando en el puerto {puerto}."


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(description="Hito 11 - limpieza opcional del diagnóstico")
    parser.add_argument("--confirmar", action="store_true", help="ejecutar la limpieza (sin esto, solo simula)")
    parser.add_argument("--puerto-temporal", type=int, default=8001)
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR")
    args = parser.parse_args(argv)

    cfg = Config(parse_overrides(args.set))
    redactar = Redactor(cfg.secretos())

    print("=== HITO 11 - LIMPIEZA OPCIONAL ===")
    print("Modo:", "EJECUCION" if args.confirmar else "SIMULACION (agregar --confirmar para ejecutar)")
    print("No se tocan datos de dominio, contenedores, volúmenes ni evidencias.")
    print()

    print(redactar(limpiar_redis(cfg, args.confirmar)))
    for linea in limpiar_archivos(args.confirmar):
        print(linea)
    print(verificar_api_temporal(args.puerto_temporal))
    return 0


if __name__ == "__main__":
    sys.exit(main())
