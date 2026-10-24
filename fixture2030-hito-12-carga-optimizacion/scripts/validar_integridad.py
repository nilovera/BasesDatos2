"""VALIDACIÓN DE INTEGRIDAD de una corrida (Hito 12, punto 5.8).

Un HTTP 200 no alcanza. Para la corrida indicada se verifica:
  1. Conteo: solicitudes generadas vs. con respuesta vs. exitosas vs. rechazadas (por causa).
  2. Identificadores únicos: ningún request_id repetido (no hubo duplicados del generador).
  3. Contenido: cada respuesta 200 se comparó con la huella del catálogo (ok / alterada / no verificable).
  4. Lado servidor: los request_id enviados aparecen en el log de la API (la API recibió lo que el
     generador dice haber enviado) y con el mismo código HTTP.
  5. Fuente después de la carga: se vuelve a leer TODO el catálogo con concurrencia 1 y se cuentan
     los datos sintéticos directamente en Redis e IRIS -> la prueba no alteró ni perdió datos.

Uso:  python validar_integridad.py <carpeta_de_la_corrida | linea_base | optimizada>
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import sys
from collections import Counter
from pathlib import Path

import httpx

import comun


def ubicar_corrida(arg: str) -> Path:
    ruta = comun.EVIDENCIA_DIR / arg
    if ruta.is_dir():
        return ruta
    candidatas = sorted(p for p in comun.EVIDENCIA_DIR.glob(f"{arg}_*") if p.is_dir())
    if not candidatas:
        raise SystemExit(f"[ERROR] No encontré corridas para '{arg}' en {comun.EVIDENCIA_DIR}")
    return candidatas[-1]


def leer_solicitudes(corrida: Path) -> list[dict]:
    with gzip.open(corrida / "solicitudes.csv.gz", "rt", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def ids_en_log_api(ids: set[str]) -> dict[str, int]:
    """request_id -> código HTTP registrado por el middleware de la API."""
    patron = re.compile(r'"request_id": "([0-9a-f-]{36})".*?"resultado": (\d+)')
    encontrados: dict[str, int] = {}
    for nombre in ("api.stdout.log", "api.stderr.log"):
        ruta = comun.API_ROOT / "logs" / nombre
        if not ruta.exists():
            continue
        with ruta.open(encoding="utf-8", errors="replace") as fh:
            for linea in fh:
                if "request_id" not in linea:
                    continue
                m = patron.search(linea)
                if m and m.group(1) in ids:
                    encontrados[m.group(1)] = int(m.group(2))
    return encontrados


def releer_catalogo(base_url: str) -> dict:
    catalogo = json.loads(comun.CATALOGO_PATH.read_text(encoding="utf-8"))["claves"]
    iguales = distintas = faltantes = 0
    detalle = Counter()
    with httpx.Client(base_url=base_url, timeout=30) as cliente:
        for e in catalogo:
            r = cliente.get(e["url"])
            if r.status_code != 200:
                faltantes += 1
                detalle[f"{e['tipo']}:http_{r.status_code}"] += 1
            elif comun.huella(r.json()) == e["huella"]:
                iguales += 1
            elif e["determinista"]:
                distintas += 1
                detalle[f"{e['tipo']}:distinta"] += 1
            else:
                iguales += 1
    return {"claves": len(catalogo), "iguales": iguales, "distintas": distintas, "faltantes": faltantes,
            "detalle": dict(detalle)}


def contar_en_fuentes() -> dict:
    out: dict = {}
    s = comun.get_settings()
    try:
        import redis
        c = redis.Redis(host=s.redis_host, port=s.redis_port, db=s.redis_database)
        out["redis_sesiones_h12"] = sum(1 for _ in c.scan_iter(match=f"sesion:{comun.PREFIJO_SESION_REDIS}*", count=500))
        c.close()
    except Exception as error:  # noqa: BLE001
        out["redis_error"] = type(error).__name__
    try:
        import iris.dbapi as iris_dbapi
        con = iris_dbapi.connect(s.iris_host, s.iris_port, s.iris_namespace, s.iris_username,
                                 s.iris_password.get_secret_value())
        cur = con.cursor()
        pref = comun.PREFIJO_PARTIDO_IRIS
        cur.execute(f"SELECT COUNT(*) FROM Fixture.Partido WHERE Codigo %STARTSWITH '{pref}'")
        out["iris_partidos_h12"] = cur.fetchall()[0][0]
        cur.execute("SELECT COUNT(*) FROM Fixture.EventoPartido e WHERE e.Partido->Codigo %STARTSWITH ?", [pref])
        out["iris_eventos_h12"] = cur.fetchall()[0][0]
        cur.close()
        con.close()
    except Exception as error:  # noqa: BLE001
        out["iris_error"] = type(error).__name__
    try:
        from cassandra.concurrent import execute_concurrent_with_args
        cfg = comun.cargar_config()
        cluster, ses = comun.sesion_cassandra()
        ids = {}
        for c in comun.comentarios_sinteticos(cfg["datos_sinteticos"]["comentarios_por_bucket_cassandra"], cfg["semilla"]):
            ids.setdefault((c["partido_id"], c["bucket_10min"]), set()).add(c["comentario_id"])
        q = ses.prepare("SELECT comentario_id FROM comentarios_por_partido WHERE partido_id=? AND bucket_10min=?")
        presentes = 0
        for (ok, filas), clave in zip(execute_concurrent_with_args(ses, q, list(ids), concurrency=32), ids):
            if ok:
                presentes += sum(1 for f in filas if f.comentario_id in ids[clave])
        cluster.shutdown()
        out["cassandra_comentarios_h12"] = presentes
    except Exception as error:  # noqa: BLE001
        out["cassandra_error"] = type(error).__name__
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    corrida = ubicar_corrida(sys.argv[1])
    cfg = comun.cargar_config()
    filas = leer_solicitudes(corrida)
    print(f"=== HITO 12 - VALIDAR INTEGRIDAD: {corrida.name} ===")

    generadas = len(filas)
    con_respuesta = sum(1 for f in filas if f["status"] != "0")
    exitosas = sum(1 for f in filas if f["error"] == "")
    rechazos = Counter(f["error"] for f in filas if f["error"])
    integ = Counter(f["integridad"] for f in filas)
    ids = [f["request_id"] for f in filas]
    duplicados = len(ids) - len(set(ids))

    log = ids_en_log_api(set(ids))
    con_resp_ids = {f["request_id"]: int(f["status"]) for f in filas if f["status"] != "0"}
    no_en_log = sum(1 for i in con_resp_ids if i not in log)
    status_distinto = sum(1 for i, st in con_resp_ids.items() if i in log and log[i] != st)

    print("Releyendo el catálogo completo con concurrencia 1 (puede tardar ~1 minuto)...")
    relectura = releer_catalogo(cfg["api_base_url"])
    fuentes = contar_en_fuentes()
    prep = json.loads(comun.CATALOGO_PATH.read_text(encoding="utf-8"))["resumen"]

    chequeos = {
        "sin_request_id_duplicados": duplicados == 0,
        "sin_respuestas_alteradas": integ.get("alterada", 0) == 0,
        "api_registro_todas_las_respuestas": no_en_log == 0,
        "mismo_codigo_http_cliente_y_api": status_distinto == 0,
        "catalogo_identico_tras_la_carga": relectura["distintas"] == 0 and relectura["faltantes"] == 0,
        "redis_sesiones_completas": fuentes.get("redis_sesiones_h12") == prep.get("sesiones_redis_sinteticas"),
        "iris_partidos_completos": fuentes.get("iris_partidos_h12") == prep.get("partidos_iris_sinteticos"),
        "cassandra_comentarios_completos": fuentes.get("cassandra_comentarios_h12") == prep.get("comentarios_cassandra_sinteticos_por_tabla"),
    }
    resultado = {
        "corrida": corrida.name, "fecha_validacion": comun.ahora_iso(),
        "conteos": {"generadas": generadas, "con_respuesta": con_respuesta, "sin_respuesta": generadas - con_respuesta,
                    "exitosas_y_correctas": exitosas, "rechazadas_por_causa": dict(rechazos)},
        "integridad_contenido": dict(integ), "request_id_duplicados": duplicados,
        "log_api": {"respuestas_cliente": len(con_resp_ids), "encontradas_en_log": len(con_resp_ids) - no_en_log,
                    "no_encontradas": no_en_log, "codigo_distinto": status_distinto},
        "relectura_catalogo_post_carga": relectura, "conteo_directo_en_fuentes": fuentes,
        "esperado_segun_preparacion": {"redis_sesiones_h12": prep.get("sesiones_redis_sinteticas"),
                                       "iris_partidos_h12": prep.get("partidos_iris_sinteticos"),
                                       "cassandra_comentarios_h12": prep.get("comentarios_cassandra_sinteticos_por_tabla")},
        "chequeos": chequeos, "aprobado": all(chequeos.values()),
    }
    comun.escribir_json(corrida / "integridad.json", resultado)

    print(f"Generadas {generadas} | con respuesta {con_respuesta} | exitosas y correctas {exitosas}")
    print(f"Rechazadas por causa: {dict(rechazos) or 'ninguna'}")
    print(f"Contenido: {dict(integ)} | request_id duplicados: {duplicados}")
    print(f"Log API: {len(con_resp_ids) - no_en_log}/{len(con_resp_ids)} encontradas, código distinto: {status_distinto}")
    print(f"Relectura del catálogo: {relectura}")
    print(f"Conteo directo en fuentes: {fuentes}")
    for nombre, ok in chequeos.items():
        print(f"  [{'OK ' if ok else 'FALLA'}] {nombre}")
    print(f"RESULTADO: {'APROBADO' if resultado['aprobado'] else 'CON OBSERVACIONES'}  -> {corrida.name}/integridad.json")
    return 0 if resultado["aprobado"] else 2


if __name__ == "__main__":
    sys.exit(main())
