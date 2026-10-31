"""Genera los archivos LOCALES que necesita el stack de monitoreo (no se versionan).

A partir del .env de la API crea:
  - .secretos/influxdb_token   token con el que Prometheus lee /metrics de InfluxDB 3
  - .secretos/iris_password    password de _SYSTEM para /api/monitor/metrics de IRIS
  - .env                       GRAFANA_ADMIN_PASSWORD (al azar) y MONGODB_EXPORTER_URI

Nunca imprime los valores. Si .env ya existe conserva la contraseña de Grafana.

Uso: .venv\\Scripts\\python.exe fixture2030-hito-13-monitoreo\\scripts\\preparar_secretos.py
"""
from __future__ import annotations

import secrets
import sys
from urllib.parse import quote

import comun_monitoreo as cm


def escribir_secreto(nombre: str, valor: str) -> None:
    carpeta = cm.HITO_DIR / ".secretos"
    carpeta.mkdir(exist_ok=True)
    # Sin salto de línea final ni BOM: Prometheus usa el contenido tal cual.
    (carpeta / nombre).write_bytes(valor.encode("utf-8"))


def main() -> int:
    api_env = cm.leer_env(cm.API_ROOT / ".env")
    if not api_env:
        print("[ERROR] No se encontró el .env de la API (copiar .env.example y completarlo, o usar entorno-local).")
        return 1

    faltan = [c for c in ("MONGODB_USERNAME", "MONGODB_PASSWORD", "INFLUXDB_TOKEN", "IRIS_PASSWORD") if not api_env.get(c)]
    if faltan:
        print(f"[AVISO] El .env de la API no tiene valor para: {', '.join(faltan)}. Los targets que lo usan quedarán DOWN.")

    escribir_secreto("influxdb_token", api_env.get("INFLUXDB_TOKEN", ""))
    escribir_secreto("iris_password", api_env.get("IRIS_PASSWORD", ""))

    env_monitoreo = cm.leer_env(cm.HITO_DIR / ".env")
    grafana = env_monitoreo.get("GRAFANA_ADMIN_PASSWORD") or secrets.token_urlsafe(18)
    usuario = quote(api_env.get("MONGODB_USERNAME", ""), safe="")
    password = quote(api_env.get("MONGODB_PASSWORD", ""), safe="")
    auth_source = api_env.get("MONGODB_AUTH_SOURCE", "admin") or "admin"
    puerto = api_env.get("MONGODB_PORT", "27017") or "27017"
    uri = f"mongodb://{usuario}:{password}@host.docker.internal:{puerto}/{auth_source}?directConnection=true"

    contenido = (
        "# Generado por scripts/preparar_secretos.py - NO versionar (está en .gitignore)\n"
        f"GRAFANA_ADMIN_PASSWORD={grafana}\n"
        f"MONGODB_EXPORTER_URI={uri}\n"
    )
    (cm.HITO_DIR / ".env").write_text(contenido, encoding="utf-8")

    print("Secretos locales listos (valores no mostrados):")
    print("  .secretos/influxdb_token, .secretos/iris_password, .env")
    print("  Usuario de Grafana: admin  |  contraseña: ver GRAFANA_ADMIN_PASSWORD en fixture2030-hito-13-monitoreo/.env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
