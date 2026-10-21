"""Fallo controlado y recuperación (Hito 11, RF17, RF20, RF21, sección 5.7).

Escenarios (reversibles, sin borrar datos ni volúmenes):

``detenida`` (por defecto)
    Detiene temporalmente el contenedor de un producto con ``docker stop``,
    observa la respuesta de la API y del diagnóstico, lo vuelve a iniciar
    con ``docker start``, repite las pruebas y compara la cantidad de datos
    antes y después. Nunca usa ``docker compose down -v`` ni ``docker rm``.

``config``
    No toca Docker. Inicia una SEGUNDA instancia temporal de la API en otro
    puerto (8001 por defecto) con una variable sobrescrita solo para ese
    proceso (por ejemplo una database inexistente o una password inválida
    de laboratorio), observa cómo responde y la detiene. La API principal y
    el archivo .env no se modifican.

Ejemplos (desde la raíz del repositorio):
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\falla_controlada.py --producto mongodb
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\falla_controlada.py --escenario config --producto neo4j --set NEO4J_DATABASE=noexiste
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

import prueba_api
import prueba_clientes_nativos
import prueba_tcp
from common import (
    EVIDENCIA_DIR,
    FALLA,
    PRODUCTOS,
    REPO_ROOT,
    Config,
    Redactor,
    ahora_iso,
    contexto_ejecucion,
    docker_disponible,
    estado_producto,
    parse_overrides,
    preparar_consola,
    resolver_contenedor,
)


RUTAS = {
    "mongodb": "/api/v1/equipos/{MONGO_EQUIPO_DEMO}",
    "neo4j": "/api/v1/partidos/{NEO4J_PARTIDO_DEMO}/eventos",
    "cassandra": "/api/v1/partidos/{CASSANDRA_PARTIDO_DEMO}/comentarios?bucket_10min={CASSANDRA_BUCKET_DEMO}&limit=3",
    "redis": "/api/v1/sesiones/{REDIS_SESION_DEMO}",
    "influxdb": "/api/v1/partidos/{INFLUX_PARTIDO_DEMO}/estadisticas?desde={INFLUX_DESDE}&hasta={INFLUX_HASTA}&limit=10",
    "iris": "/api/v1/partidos/{IRIS_PARTIDO_DEMO}/detalle",
}


def ruta(cfg: Config, producto: str) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: cfg.get(m.group(1), ""), RUTAS[producto])


# --------------------------------------------------------------------------
# Lectura de cantidad de datos (solo lectura) para comprobar persistencia
# --------------------------------------------------------------------------

def conteo_datos(cfg: Config, producto: str) -> dict:
    t = cfg.timeout
    try:
        if producto == "mongodb":
            from pymongo import MongoClient

            c = MongoClient(
                host=cfg.get("MONGODB_HOST"), port=cfg.get_int("MONGODB_PORT", 27017),
                username=cfg.get("MONGODB_USERNAME"), password=cfg.get("MONGODB_PASSWORD"),
                authSource=cfg.get("MONGODB_AUTH_SOURCE"), serverSelectionTimeoutMS=int(t * 1000),
            )
            try:
                db = c[cfg.get("MONGODB_DATABASE")]
                return {"equipos": db.equipos.count_documents({}), "jugadores": db.jugadores.count_documents({})}
            finally:
                c.close()
        if producto == "neo4j":
            from neo4j import GraphDatabase

            d = GraphDatabase.driver(cfg.get("NEO4J_URI"), auth=(cfg.get("NEO4J_USERNAME"), cfg.get("NEO4J_PASSWORD")),
                                     connection_timeout=t)
            try:
                with d.session(database=cfg.get("NEO4J_DATABASE")) as s:
                    r = s.run("MATCH (n) RETURN count(n) AS nodos").single()
                    r2 = s.run("MATCH ()-[x]->() RETURN count(x) AS relaciones").single()
                return {"nodos": r["nodos"], "relaciones": r2["relaciones"]}
            finally:
                d.close()
        if producto == "cassandra":
            from cassandra.cluster import Cluster

            cl = Cluster(cfg.get("CASSANDRA_HOSTS").split(","), port=cfg.get_int("CASSANDRA_PORT", 9042),
                         connect_timeout=t, control_connection_timeout=t)
            try:
                s = cl.connect(cfg.get("CASSANDRA_KEYSPACE"))
                filas = s.execute(
                    f"SELECT COUNT(*) AS n FROM {cfg.get('CASSANDRA_TABLA')} WHERE partido_id=%s AND bucket_10min=%s",
                    [cfg.get("CASSANDRA_PARTIDO_DEMO"), cfg.get("CASSANDRA_BUCKET_DEMO")], timeout=t * 3,
                ).one()
                return {"comentarios_particion_demo": filas.n}
            finally:
                cl.shutdown()
        if producto == "redis":
            import redis

            r = redis.Redis(host=cfg.get("REDIS_HOST"), port=cfg.get_int("REDIS_PORT", 6379),
                            db=cfg.get_int("REDIS_DATABASE", 0), password=cfg.get("REDIS_PASSWORD"),
                            socket_connect_timeout=t, socket_timeout=t)
            try:
                return {"claves_db": r.dbsize(), "sesiones": sum(1 for _ in r.scan_iter("sesion:*", count=500))}
            finally:
                r.close()
        if producto == "influxdb":
            import httpx

            resp = httpx.post(
                cfg.get("INFLUXDB_URL").rstrip("/") + "/api/v3/query_sql",
                headers={"Authorization": f"Bearer {cfg.get('INFLUXDB_TOKEN')}"},
                json={"db": cfg.get("INFLUXDB_DETAIL_DATABASE"), "format": "json",
                      "q": f"SELECT COUNT(*) AS puntos FROM {cfg.get('INFLUX_TABLA_DETALLE')}"},
                timeout=t * 3, trust_env=False,
            )
            resp.raise_for_status()
            filas = resp.json()
            return {"puntos_detalle": filas[0]["puntos"] if filas else 0}
        if producto == "iris":
            import iris.dbapi as iris_dbapi

            conn = iris_dbapi.connect(cfg.get("IRIS_HOST"), cfg.get_int("IRIS_PORT", 1972), cfg.get("IRIS_NAMESPACE"),
                                      cfg.get("IRIS_USERNAME"), cfg.get("IRIS_PASSWORD"), timeout=max(1, int(t)))
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM Fixture.Partido")
                partidos = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM Fixture.EventoPartido")
                eventos = cur.fetchone()[0]
                return {"partidos": partidos, "eventos": eventos}
            finally:
                conn.close()
    except Exception as error:  # noqa: BLE001
        return {"error": type(error).__name__}
    return {}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def docker(*args: str, timeout: int = 60) -> tuple[int, str]:
    out = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)
    return out.returncode, (out.stdout + out.stderr).strip()


def montajes(contenedor: str) -> list[str]:
    rc, salida = docker(
        "inspect", "--format",
        "{{range .Mounts}}{{.Type}}:{{if .Name}}{{.Name}}{{else}}{{.Source}}{{end}}->{{.Destination}};{{end}}",
        contenedor,
    )
    return [m for m in salida.split(";") if m] if rc == 0 else []


def llamar_api(base: str, path: str, log_file: Path, redactar: Redactor, timeout: float) -> dict:
    import httpx

    rid = str(uuid.uuid4())
    inicio = time.perf_counter()
    try:
        r = httpx.get(base.rstrip("/") + path, headers={"X-Request-ID": rid}, timeout=timeout, trust_env=False)
        dur = round((time.perf_counter() - inicio) * 1000, 2)
        try:
            body = r.json()
        except Exception:
            body = {"texto": r.text[:200]}
        clase, interp = prueba_api.clasificar_respuesta(r.status_code, body, False)
        resultado = {
            "status": r.status_code, "tiempo_ms": dur, "request_id": rid,
            "x_process_time_ms": r.headers.get("x-process-time-ms"),
            "resumen": prueba_api.resumir(body), "clasificacion": clase, "interpretacion": interp,
        }
    except Exception as error:  # noqa: BLE001
        dur = round((time.perf_counter() - inicio) * 1000, 2)
        resultado = {"status": None, "tiempo_ms": dur, "request_id": rid,
                     "clasificacion": "api_no_alcanzable", "interpretacion": f"{type(error).__name__}"}
    time.sleep(0.3)
    lineas = prueba_api.buscar_log(log_file, [rid]).get(rid, [])
    resultado["log"] = [redactar(l) for l in lineas[-3:]] or ["(sin línea de log encontrada)"]
    resultado["path"] = path
    return resultado


def diag_producto(cfg: Config, producto: str, redactar: Redactor) -> dict:
    tcp = [r for r in prueba_tcp.evaluar(cfg, [producto], redactar, incluir_api=False) if r.capa in ("proceso", "tcp")]
    nativos = prueba_clientes_nativos.evaluar(cfg, [producto], redactar, permitir_escritura=False)
    todos = tcp + nativos
    estado, motivo = estado_producto(todos)
    primera_falla = next((r for r in todos if r.requerida and r.estado == FALLA), None)
    return {
        "estado": estado,
        "motivo": motivo,
        "capa_que_falla": primera_falla.capa if primera_falla else None,
        "clasificacion": primera_falla.clasificacion if primera_falla else None,
        "pruebas": [
            {"capa": r.capa, "prueba": r.prueba, "estado": r.estado, "clasificacion": r.clasificacion,
             "duracion_ms": r.duracion_ms, "detalle": r.detalle[:200]}
            for r in todos
        ],
    }


def health(base: str, timeout: float) -> dict:
    import httpx

    try:
        r = httpx.get(base.rstrip("/") + "/health/dependencias", params={"refrescar": "true"},
                      timeout=timeout, trust_env=False)
        body = r.json()
        return {"estado_general": body.get("estado_general"),
                "dependencias": {d["dependencia"]: f"{d['estado']} ({d['clasificacion']})" for d in body.get("dependencias", [])}}
    except Exception as error:  # noqa: BLE001
        return {"error": type(error).__name__}


def esperar_recuperacion(cfg: Config, producto: str, redactar: Redactor, limite_s: int) -> tuple[bool, float, int]:
    inicio = time.perf_counter()
    intentos = 0
    while time.perf_counter() - inicio < limite_s:
        intentos += 1
        res = prueba_clientes_nativos.evaluar(cfg, [producto], redactar, permitir_escritura=False)
        if estado_producto(res)[0] in ("disponible", "degradado"):
            return True, round(time.perf_counter() - inicio, 1), intentos
        time.sleep(3)
    return False, round(time.perf_counter() - inicio, 1), intentos


def otro_producto_disponible(cfg: Config, excluir: str, redactar: Redactor) -> str | None:
    for clave in ["redis", "mongodb", "neo4j", "influxdb", "iris", "cassandra"]:
        if clave == excluir:
            continue
        res = prueba_clientes_nativos.evaluar(cfg, [clave], redactar, permitir_escritura=False)
        if estado_producto(res)[0] in ("disponible", "degradado"):
            return clave
    return None


def bloque_api(titulo: str, llamada: dict) -> list[str]:
    lineas = [
        f"- **{titulo}:** `GET {llamada['path']}` → HTTP **{llamada['status']}** en {llamada['tiempo_ms']} ms "
        f"({llamada['clasificacion']}). {llamada.get('interpretacion', '')}",
        f"  - request_id: `{llamada['request_id']}` · resumen: {llamada.get('resumen', '-')}",
    ]
    for l in llamada.get("log", []):
        lineas.append(f"  - log: `{l[:260]}`")
    return lineas


# --------------------------------------------------------------------------
# Escenario: dependencia detenida
# --------------------------------------------------------------------------

def escenario_detenida(cfg: Config, producto: str, redactar: Redactor, limite_recuperacion: int) -> dict:
    nombre = PRODUCTOS[producto]["nombre"]
    base = cfg.get("API_BASE_URL")
    log_file = REPO_ROOT / (cfg.get("API_LOG_FILE") or "logs/api.stderr.log")
    timeout_api = cfg.get_float("DEPENDENCY_TIMEOUT_SECONDS", 5) + 5

    if not docker_disponible():
        raise SystemExit("Docker CLI no disponible: el escenario 'detenida' requiere Docker.")
    contenedor = resolver_contenedor(cfg, producto)
    if not contenedor:
        raise SystemExit(f"No se encontró en ejecución el contenedor de {nombre} ({cfg.contenedor(producto)}).")

    reg: dict = {"escenario": "dependencia detenida", "producto": nombre, "contenedor": contenedor}
    print(f"=== FALLA CONTROLADA: {nombre} detenido temporalmente ({contenedor}) ===")

    print("[1/6] Condición inicial...")
    control = otro_producto_disponible(cfg, producto, redactar)
    reg["producto_control"] = PRODUCTOS[control]["nombre"] if control else None
    reg["inicial"] = {
        "fecha": ahora_iso(),
        "estado_contenedor": docker("inspect", "--format", "{{.State.Status}}", contenedor)[1],
        "montajes": montajes(contenedor),
        "datos": conteo_datos(cfg, producto),
        "diagnostico": diag_producto(cfg, producto, redactar),
        "api": llamar_api(base, ruta(cfg, producto), log_file, redactar, timeout_api),
        "api_control": llamar_api(base, ruta(cfg, control), log_file, redactar, timeout_api) if control else None,
        "health": health(base, timeout_api),
    }

    try:
        print(f"[2/6] Cambio aplicado: docker stop {contenedor} (sin borrar volúmenes)...")
        inicio = time.perf_counter()
        rc, salida = docker("stop", contenedor, timeout=90)
        reg["cambio"] = {
            "comando": f"docker stop {contenedor}",
            "rc": rc,
            "duracion_s": round(time.perf_counter() - inicio, 1),
            "fecha": ahora_iso(),
        }
        time.sleep(2)

        print("[3/6] Pruebas durante la falla...")
        time.sleep(5.5)  # supera el intervalo mínimo de refresco del health
        reg["durante"] = {
            "fecha": ahora_iso(),
            "estado_contenedor": docker("inspect", "--format", "{{.State.Status}}", contenedor)[1],
            "diagnostico": diag_producto(cfg, producto, redactar),
            "api": llamar_api(base, ruta(cfg, producto), log_file, redactar, timeout_api),
            "api_control": llamar_api(base, ruta(cfg, control), log_file, redactar, timeout_api) if control else None,
            "health": health(base, timeout_api),
        }
    finally:
        print(f"[4/6] Recuperación: docker start {contenedor}...")
        rc, salida = docker("start", contenedor, timeout=90)
        ok, segundos, intentos = esperar_recuperacion(cfg, producto, redactar, limite_recuperacion)
        reg["recuperacion"] = {
            "comando": f"docker start {contenedor}",
            "rc": rc,
            "recuperado": ok,
            "segundos_hasta_disponible": segundos,
            "intentos": intentos,
            "fecha": ahora_iso(),
        }

    print("[5/6] Pruebas después de recuperar...")
    time.sleep(5.5)
    despues_api = llamar_api(base, ruta(cfg, producto), log_file, redactar, timeout_api)
    if despues_api["status"] != 200:
        # Algunos drivers (ej. Cassandra) restablecen el pool en segundo plano.
        time.sleep(10)
        despues_api = llamar_api(base, ruta(cfg, producto), log_file, redactar, timeout_api)
    reg["despues"] = {
        "fecha": ahora_iso(),
        "estado_contenedor": docker("inspect", "--format", "{{.State.Status}}", contenedor)[1],
        "montajes": montajes(contenedor),
        "datos": conteo_datos(cfg, producto),
        "diagnostico": diag_producto(cfg, producto, redactar),
        "api": despues_api,
        "health": health(base, timeout_api),
    }

    print("[6/6] Comparación de datos y volúmenes...")
    reg["datos_conservados"] = (
        reg["inicial"]["datos"] == reg["despues"]["datos"] and "error" not in reg["inicial"]["datos"]
    )
    reg["volumenes_conservados"] = reg["inicial"]["montajes"] == reg["despues"]["montajes"]
    return reg


def markdown_detenida(reg: dict, contexto: dict) -> str:
    ini, dur, rec, des = reg["inicial"], reg.get("durante", {}), reg["recuperacion"], reg["despues"]
    lineas = [
        f"# Falla controlada: {reg['producto']} detenido temporalmente",
        "",
        f"> Generado por `scripts/falla_controlada.py` el {contexto['fecha']} · commit `{contexto['commit']}` · "
        f"entorno: {contexto['entorno']}.",
        "",
        "## 1. Condición inicial",
        "",
        f"- Contenedor `{reg['contenedor']}`: **{ini['estado_contenedor']}**.",
        f"- Montajes/volúmenes: {', '.join(f'`{m}`' for m in ini['montajes']) or '-'}",
        f"- Datos (lectura): `{json.dumps(ini['datos'], ensure_ascii=False)}`",
        f"- Diagnóstico nativo: **{ini['diagnostico']['estado']}** — {ini['diagnostico']['motivo']}",
        f"- Health de la API: {ini['health']}",
        *bloque_api("Ruta del producto", ini["api"]),
    ]
    if ini.get("api_control"):
        lineas += bloque_api(f"Ruta de control ({reg['producto_control']})", ini["api_control"])
    lineas += [
        "",
        "## 2. Cambio aplicado",
        "",
        f"- Comando: `{reg['cambio']['comando']}` (rc={reg['cambio']['rc']}, {reg['cambio']['duracion_s']} s, {reg['cambio']['fecha']}).",
        "- No se usó `docker compose down -v`, `docker rm` ni ningún borrado de datos o volúmenes.",
        "",
        "## 3. Prueba ejecutada durante la falla",
        "",
    ]
    if dur:
        d = dur["diagnostico"]
        lineas += [
            f"- Contenedor: **{dur['estado_contenedor']}**.",
            f"- Diagnóstico nativo: **{d['estado']}** — capa que falla: `{d['capa_que_falla']}` ({d['clasificacion']}).",
            f"- Health de la API: {dur['health']}",
            "",
            "## 4. Respuesta de la API, mensaje de log y tiempo de espera",
            "",
            *bloque_api("Ruta del producto caído", dur["api"]),
        ]
        if dur.get("api_control"):
            lineas += bloque_api(f"Ruta de control ({reg['producto_control']})", dur["api_control"])
        espera = dur["api"]["tiempo_ms"]
        if espera < 1000:
            explicacion = (
                f"La API respondió en {espera} ms: el puerto rechazó la conexión (connection refused) y el "
                "adaptador lo informó de inmediato, sin reintentos. Si la falla fuera un timeout de red, la "
                "espera quedaría acotada por `DEPENDENCY_TIMEOUT_SECONDS` (RNF5, RNF12)."
            )
        else:
            explicacion = (
                f"La API respondió en {espera} ms: el driver esperó hasta agotar su límite "
                "(`DEPENDENCY_TIMEOUT_SECONDS` / selección de servidor) y luego devolvió un error identificable. "
                "La request no quedó bloqueada indefinidamente ni se reintentó en bucle (RNF5, RNF12)."
            )
        lineas += ["", explicacion]
    lineas += [
        "",
        "## 5. Recuperación del servicio",
        "",
        f"- Comando: `{rec['comando']}` (rc={rec['rc']}).",
        f"- Recuperado: **{'sí' if rec['recuperado'] else 'no'}** — {rec['segundos_hasta_disponible']} s hasta que el "
        f"diagnóstico nativo volvió a terminar OK ({rec['intentos']} intentos).",
        "",
        "## 6. Resultado después de recuperar la dependencia",
        "",
        f"- Diagnóstico nativo: **{des['diagnostico']['estado']}** — {des['diagnostico']['motivo']}",
        f"- Health de la API: {des['health']}",
        *bloque_api("Ruta del producto", des["api"]),
        "",
        "## 7. Datos y volúmenes conservados",
        "",
        f"- Datos antes: `{json.dumps(ini['datos'], ensure_ascii=False)}` · después: `{json.dumps(des['datos'], ensure_ascii=False)}` "
        f"→ **{'conservados' if reg['datos_conservados'] else 'REVISAR'}**.",
        f"- Volúmenes antes/después iguales: **{'sí' if reg['volumenes_conservados'] else 'REVISAR'}**.",
        "",
        "## Cambio de estado (RF20)",
        "",
        "| Momento | Diagnóstico nativo | Ruta de la API | Health |",
        "|---|---|---|---|",
        f"| Inicial | {ini['diagnostico']['estado']} | HTTP {ini['api']['status']} | {ini['health'].get('estado_general')} |",
    ]
    if dur:
        lineas.append(
            f"| Durante | {dur['diagnostico']['estado']} | HTTP {dur['api']['status']} | {dur['health'].get('estado_general')} |"
        )
    lineas.append(
        f"| Después | {des['diagnostico']['estado']} | HTTP {des['api']['status']} | {des['health'].get('estado_general')} |"
    )
    lineas.append("")
    return "\n".join(lineas)


# --------------------------------------------------------------------------
# Escenario: configuración incorrecta en una instancia temporal de la API
# --------------------------------------------------------------------------

def escenario_config(cfg: Config, producto: str, overrides: dict, redactar: Redactor, puerto: int) -> dict:
    if not overrides:
        raise SystemExit("El escenario 'config' necesita al menos un --set CLAVE=VALOR (ej. NEO4J_DATABASE=noexiste).")

    nombre = PRODUCTOS[producto]["nombre"]
    base_temp = f"http://127.0.0.1:{puerto}"
    log_file = REPO_ROOT / "logs" / f"api_falla_{puerto}.stderr.log"
    log_file.parent.mkdir(exist_ok=True)
    timeout_api = cfg.get_float("DEPENDENCY_TIMEOUT_SECONDS", 5) + 5
    claves = ", ".join(overrides)

    reg: dict = {"escenario": "configuración incorrecta", "producto": nombre, "variables": claves, "puerto": puerto}
    print(f"=== FALLA CONTROLADA: {nombre} con configuración incorrecta ({claves}) en API temporal :{puerto} ===")

    cfg_mal = Config(overrides)
    reg["diagnostico_nativo_con_override"] = diag_producto(cfg_mal, producto, Redactor(cfg_mal.secretos()))
    reg["api_principal_antes"] = llamar_api(cfg.get("API_BASE_URL"), ruta(cfg, producto),
                                            REPO_ROOT / (cfg.get("API_LOG_FILE") or "logs/api.stderr.log"), redactar, timeout_api)

    env = dict(os.environ)
    env.update(overrides)
    env["PYTHONIOENCODING"] = "utf-8"
    with open(log_file, "w", encoding="utf-8") as err:
        proceso = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(puerto)],
            cwd=REPO_ROOT, env=env, stdout=subprocess.DEVNULL, stderr=err,
        )
    reg["cambio"] = {
        "descripcion": f"API temporal en :{puerto} con {claves} sobrescrito solo en el entorno de ese proceso",
        "fecha": ahora_iso(),
    }
    try:
        import httpx

        listo = False
        for _ in range(40):
            time.sleep(0.5)
            try:
                if httpx.get(base_temp + "/health/live", timeout=1, trust_env=False).status_code == 200:
                    listo = True
                    break
            except Exception:
                pass
        reg["api_temporal_iniciada"] = listo
        if listo:
            reg["api_temporal"] = llamar_api(base_temp, ruta(cfg, producto), log_file, redactar, timeout_api)
            reg["health_temporal"] = health(base_temp, timeout_api)
    finally:
        proceso.terminate()
        try:
            proceso.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proceso.kill()
        reg["recuperacion"] = {"descripcion": f"API temporal :{puerto} detenida; .env sin cambios", "fecha": ahora_iso()}

    reg["api_principal_despues"] = llamar_api(cfg.get("API_BASE_URL"), ruta(cfg, producto),
                                              REPO_ROOT / (cfg.get("API_LOG_FILE") or "logs/api.stderr.log"), redactar, timeout_api)
    return reg


def markdown_config(reg: dict, contexto: dict) -> str:
    d = reg["diagnostico_nativo_con_override"]
    lineas = [
        f"# Falla controlada: {reg['producto']} con configuración incorrecta",
        "",
        f"> Generado por `scripts/falla_controlada.py --escenario config` el {contexto['fecha']} · "
        f"commit `{contexto['commit']}`. Valores sobrescritos no mostrados.",
        "",
        "## 1. Condición inicial",
        "",
        *bloque_api("API principal", reg["api_principal_antes"]),
        "",
        "## 2. Cambio aplicado",
        "",
        f"- {reg['cambio']['descripcion']} ({reg['cambio']['fecha']}).",
        "- El archivo `.env` y la API principal no se modificaron.",
        "",
        "## 3. Prueba ejecutada",
        "",
        f"- Diagnóstico nativo con la misma variable sobrescrita: **{d['estado']}** — capa que falla: "
        f"`{d['capa_que_falla']}` ({d['clasificacion']}).",
        "",
        "## 4. Respuesta de la API temporal y log",
        "",
    ]
    if reg.get("api_temporal_iniciada"):
        lineas += bloque_api("API temporal", reg["api_temporal"])
        lineas.append(f"- Health de la API temporal: {reg.get('health_temporal')}")
    else:
        lineas.append("- La API temporal no llegó a iniciar: revisar el log de la instancia temporal.")
    lineas += [
        "",
        "## 5. Recuperación",
        "",
        f"- {reg['recuperacion']['descripcion']} ({reg['recuperacion']['fecha']}).",
        *bloque_api("API principal después", reg["api_principal_despues"]),
        "",
        "## 6. Datos conservados",
        "",
        "- El escenario no ejecuta escrituras ni modifica contenedores: datos y volúmenes no se tocan.",
        "",
    ]
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(description="Hito 11 - fallo controlado y recuperación")
    parser.add_argument("--escenario", default="detenida", choices=["detenida", "config"])
    parser.add_argument("--producto", default="mongodb", choices=list(PRODUCTOS))
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR")
    parser.add_argument("--puerto-temporal", type=int, default=8001)
    parser.add_argument("--limite-recuperacion", type=int, default=180,
                        help="segundos máximos esperando que el producto vuelva (Cassandra puede tardar ~1 min)")
    args = parser.parse_args(argv)

    overrides = parse_overrides(args.set)
    cfg = Config()
    secretos_override = [
        valor for clave, valor in overrides.items()
        if any(t in clave for t in ("PASSWORD", "TOKEN", "SECRET")) and len(valor) >= 3
    ]
    redactar = Redactor(cfg.secretos() + secretos_override)
    contexto = contexto_ejecucion(cfg, f"falla_{args.escenario}")

    if args.escenario == "detenida":
        reg = escenario_detenida(cfg, args.producto, redactar, args.limite_recuperacion)
        md = markdown_detenida(reg, contexto)
    else:
        reg = escenario_config(cfg, args.producto, overrides, redactar, args.puerto_temporal)
        md = markdown_config(reg, contexto)

    EVIDENCIA_DIR.mkdir(parents=True, exist_ok=True)
    base = EVIDENCIA_DIR / f"falla_controlada_{args.escenario}_{args.producto}"
    base.with_suffix(".json").write_text(
        redactar(json.dumps({"contexto": contexto, **reg}, ensure_ascii=False, indent=2, default=str)) + "\n",
        encoding="utf-8",
    )
    base.with_suffix(".md").write_text(redactar(md), encoding="utf-8")
    print()
    print(redactar(md))
    print(f"Evidencia: {base.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
