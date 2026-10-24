"""PROTOTIPO DE DATA MART (Hito 12, RF12-RF13) - extracción, transformación y carga.

Pregunta analítica:
    "¿En qué ventanas de 10 minutos de cada partido se concentra la actividad de los hinchas
     (comentarios, likes, moderación) y qué eventos del partido ocurrieron en esa ventana?"

Grano del hecho principal: UNA FILA POR PARTIDO Y VENTANA DE 10 MINUTOS.

Fuentes (se leen directo con los drivers, en lote; NO a través de la API operacional):
    Neo4j     -> partidos, equipos que lo disputan, sede y eventos (minuto, tipo)   [dim_partido, eventos]
    MongoDB   -> atributos de equipo (confederación, ranking, nombre)               [dim_equipo]
    Cassandra -> comentarios por (partido, bucket de 10 min)                        [medidas de actividad]
    InfluxDB  -> estadísticas cada 10 s agregadas a ventanas de 10 min               [fact_estadistica_ventana]
Redis (sesiones con TTL) e IRIS (detalle de partido) NO se incluyen: ver docs/integracion_data_mart.md.

Destino: SQLite (datos-o-generadores/data_mart_fixture.sqlite), un esquema dimensional relacional.
Estrategia: recarga completa e idempotente dentro de una transacción, identificada con un lote_id,
con validación de conteos fuente vs. destino antes de publicar (si falla, se hace rollback).

Uso:  python construir_data_mart.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta

import httpx

import comun

DB_PATH = comun.DATOS_DIR / "data_mart_fixture.sqlite"
VENTANAS = 15            # 18:00 a 20:30 -> 120 min de actividad + margen para alargue/datos tardíos
TIPOS_GOL = {"Gol", "Penal"}
TIPOS_TARJETA = {"Tarjeta amarilla", "Tarjeta roja"}

ESQUEMA = """
DROP TABLE IF EXISTS fact_actividad_ventana;
DROP TABLE IF EXISTS fact_estadistica_ventana;
DROP TABLE IF EXISTS dim_partido;
DROP TABLE IF EXISTS dim_equipo;
CREATE TABLE IF NOT EXISTS control_lotes (
    lote_id TEXT PRIMARY KEY, inicio TEXT, fin TEXT, estado TEXT,
    conteos_fuente TEXT, conteos_destino TEXT, validaciones TEXT, duracion_s REAL
);
CREATE TABLE dim_equipo (
    equipo_id TEXT PRIMARY KEY,          -- EQ-01 .. EQ-64 (clave común Neo4j / MongoDB)
    nombre TEXT,                         -- fuente de verdad del nombre: Neo4j
    nombre_mongodb TEXT,                 -- se conserva para auditar el conflicto
    conflicto_nombre INTEGER,            -- 1 si Neo4j y MongoDB informan nombres distintos
    confederacion TEXT, ranking INTEGER,
    lote_id TEXT
);
CREATE TABLE dim_partido (
    partido_id TEXT PRIMARY KEY, fecha_neo4j TEXT, dia_actividad TEXT, fase TEXT, sede TEXT,
    equipo_a_id TEXT REFERENCES dim_equipo(equipo_id), equipo_b_id TEXT REFERENCES dim_equipo(equipo_id),
    lote_id TEXT
);
CREATE TABLE fact_actividad_ventana (
    partido_id TEXT NOT NULL REFERENCES dim_partido(partido_id),
    ventana INTEGER NOT NULL,            -- 0 = minutos 0-9, 1 = 10-19, ...
    bucket_10min TEXT NOT NULL,          -- clave de origen en Cassandra (procedencia)
    comentarios INTEGER NOT NULL, comentarios_visibles INTEGER NOT NULL,
    comentarios_pendientes INTEGER NOT NULL, likes INTEGER NOT NULL,
    eventos INTEGER NOT NULL, goles INTEGER NOT NULL, tarjetas INTEGER NOT NULL,
    tipos_evento TEXT,
    fuentes TEXT NOT NULL, lote_id TEXT NOT NULL,
    PRIMARY KEY (partido_id, ventana)
);
CREATE INDEX ix_fact_comentarios ON fact_actividad_ventana(comentarios DESC);
CREATE TABLE fact_estadistica_ventana (
    partido_id TEXT NOT NULL, ventana_inicio TEXT NOT NULL, equipo_fuente TEXT NOT NULL,
    equipo_conciliado INTEGER NOT NULL,  -- 1 si el código de InfluxDB coincide con un equipo del partido en Neo4j
    posesion_promedio REAL, pases INTEGER, tiros_max INTEGER, muestras INTEGER,
    fuentes TEXT NOT NULL, lote_id TEXT NOT NULL,
    PRIMARY KEY (partido_id, ventana_inicio, equipo_fuente)
);
"""


# ------------------------------------------------------------------ EXTRACCIÓN
def extraer_neo4j(s) -> list[dict]:
    from neo4j import GraphDatabase
    q = """
    MATCH (p:Partido)
    OPTIONAL MATCH (p)-[:DISPUTA]->(e:Equipo)
    WITH p, collect(DISTINCT e {.codigo, .nombre, .confederacion}) AS equipos
    OPTIONAL MATCH (p)-[:SE_JUEGA_EN]->(s:Sede)
    WITH p, equipos, head(collect(s.nombre)) AS sede
    OPTIONAL MATCH (ev:Evento)-[:OCURRE_EN]->(p)
    RETURN p.codigo AS partido, toString(p.fecha) AS fecha, p.fase AS fase, sede, equipos,
           collect(ev {.codigo, .tipo, .minuto}) AS eventos
    ORDER BY partido
    """
    drv = GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_username, s.neo4j_password.get_secret_value()))
    with drv.session(database=s.neo4j_database) as ses:
        filas = [r.data() for r in ses.run(q)]
    drv.close()
    return filas


def extraer_mongo(s) -> dict[str, dict]:
    from pymongo import MongoClient
    c = MongoClient(host=s.mongodb_host, port=s.mongodb_port, username=s.mongodb_username,
                    password=s.mongodb_password.get_secret_value(), authSource=s.mongodb_auth_source,
                    serverSelectionTimeoutMS=5000)
    equipos = {d["_id"]: d for d in c[s.mongodb_database]["equipos"].find({}, {"nombre": 1, "confederacion": 1, "ranking": 1})}
    c.close()
    return equipos


def bucket_de(partido: str, ventana: int) -> tuple[str, str]:
    """Misma regla que el generador del Hito 6: 8 partidos por día, actividad desde las 18:00."""
    n = int(partido.split("-")[1])
    dia = datetime(2030, 6, 13) + timedelta(days=(n - 1) // 8)
    inicio = dia.replace(hour=18) + timedelta(minutes=10 * ventana)
    return inicio.strftime("%Y%m%d%H%M"), dia.strftime("%Y-%m-%d")


def extraer_cassandra(partidos: list[str]) -> tuple[dict, int]:
    from cassandra.concurrent import execute_concurrent_with_args
    cluster, ses = comun.sesion_cassandra()
    q = ses.prepare("SELECT estado_moderacion, likes FROM comentarios_por_partido WHERE partido_id=? AND bucket_10min=?")
    q.fetch_size = 5000
    claves = [(p, bucket_de(p, v)[0]) for p in partidos for v in range(VENTANAS)]
    agregados, filas_leidas = {}, 0
    for (ok, filas), clave in zip(execute_concurrent_with_args(ses, q, claves, concurrency=32), claves):
        if not ok:
            raise RuntimeError(f"Cassandra falló en {clave}: {filas}")
        a = {"comentarios": 0, "visibles": 0, "pendientes": 0, "likes": 0}
        for f in filas:
            a["comentarios"] += 1
            a["visibles"] += f.estado_moderacion == "visible"
            a["pendientes"] += f.estado_moderacion == "pendiente"
            a["likes"] += f.likes or 0
        filas_leidas += a["comentarios"]
        agregados[clave] = a
    cluster.shutdown()
    return agregados, filas_leidas


def extraer_influx(s) -> list[dict]:
    q = ("SELECT partido_id, equipo_id, date_bin(INTERVAL '10 minutes', time) AS ventana_inicio, "
         "avg(posesion_pct) AS posesion, sum(pases_intervalo) AS pases, max(tiros_acumulados) AS tiros, "
         "count(*) AS muestras FROM estadisticas_equipo GROUP BY partido_id, equipo_id, ventana_inicio "
         "ORDER BY partido_id, ventana_inicio, equipo_id")
    r = httpx.post(f"{s.influxdb_url.rstrip('/')}/api/v3/query_sql", timeout=30,
                   headers={"Authorization": f"Bearer {s.influxdb_token.get_secret_value()}", "Accept": "application/json"},
                   json={"db": s.influxdb_detail_database, "q": q, "format": "json"})
    r.raise_for_status()
    return r.json()


# ------------------------------------------------------------------ TRANSFORMACIÓN + CARGA
def main() -> int:
    s = comun.get_settings()
    lote = f"DM-{datetime.now(comun.TZ):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    t0 = time.perf_counter()
    inicio = comun.ahora_iso()
    print(f"=== HITO 12 - CONSTRUIR DATA MART (lote {lote}) ===")

    neo = extraer_neo4j(s)
    print(f"Neo4j: {len(neo)} partidos, {sum(len(p['eventos']) for p in neo)} eventos")
    mongo = extraer_mongo(s)
    print(f"MongoDB: {len(mongo)} equipos")
    partidos = [p["partido"] for p in neo]
    cass, filas_cass = extraer_cassandra(partidos)
    print(f"Cassandra: {len(cass)} particiones leídas, {filas_cass} comentarios")
    try:
        influx = extraer_influx(s)
        print(f"InfluxDB: {len(influx)} filas agregadas por ventana de 10 min")
    except Exception as error:  # noqa: BLE001
        influx = []
        print(f"[AVISO] InfluxDB no disponible para el lote ({type(error).__name__}); se publica sin estadísticas")

    # dim_equipo: Neo4j es la fuente de verdad del nombre; MongoDB aporta confederación y ranking
    equipos: dict[str, dict] = {}
    for p in neo:
        for e in p["equipos"]:
            equipos.setdefault(e["codigo"], {"nombre": e.get("nombre"), "conf_neo4j": e.get("confederacion")})
    for codigo, d in mongo.items():
        equipos.setdefault(codigo, {"nombre": None, "conf_neo4j": None})
    filas_equipo = []
    for codigo, d in sorted(equipos.items()):
        m = mongo.get(codigo, {})
        nombre = d["nombre"] or m.get("nombre")
        filas_equipo.append((codigo, nombre, m.get("nombre"), int(bool(m.get("nombre")) and m.get("nombre") != nombre),
                             m.get("confederacion") or d["conf_neo4j"], m.get("ranking"), lote))

    filas_partido, filas_fact, eventos_cargados, fechas_distintas = [], [], 0, 0
    equipos_partido: dict[str, set] = {}
    for p in neo:
        eq = sorted(e["codigo"] for e in p["equipos"])
        equipos_partido[p["partido"]] = {(e.get("nombre") or "").upper() for e in p["equipos"]}
        _, dia = bucket_de(p["partido"], 0)
        fechas_distintas += (p["fecha"] or "")[:10] != dia
        filas_partido.append((p["partido"], p["fecha"], dia, p["fase"], p["sede"],
                              eq[0] if eq else None, eq[1] if len(eq) > 1 else None, lote))
        por_ventana = defaultdict(list)
        for ev in p["eventos"]:
            if ev.get("minuto") is None:
                continue
            por_ventana[min(int(ev["minuto"]) // 10, VENTANAS - 1)].append(ev["tipo"])
        for v in range(VENTANAS):
            bucket, _ = bucket_de(p["partido"], v)
            a = cass[(p["partido"], bucket)]
            tipos = por_ventana.get(v, [])
            eventos_cargados += len(tipos)
            filas_fact.append((p["partido"], v, bucket, a["comentarios"], a["visibles"], a["pendientes"], a["likes"],
                               len(tipos), sum(t in TIPOS_GOL for t in tipos), sum(t in TIPOS_TARJETA for t in tipos),
                               ",".join(tipos) or None, "cassandra+neo4j", lote))

    filas_stats = []
    for r in influx:
        nombre_eq = str(r["equipo_id"]).upper()
        conciliado = any(nombre_eq[:3] == n[:3] for n in equipos_partido.get(r["partido_id"], set()))
        filas_stats.append((r["partido_id"], str(r["ventana_inicio"]), r["equipo_id"], int(conciliado),
                            round(float(r["posesion"]), 2), int(r["pases"]), int(r["tiros"]), int(r["muestras"]),
                            "influxdb", lote))

    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(ESQUEMA)
        with con:  # una transacción: o se publica todo el lote o nada
            con.executemany("INSERT INTO dim_equipo VALUES (?,?,?,?,?,?,?)", filas_equipo)
            con.executemany("INSERT INTO dim_partido VALUES (?,?,?,?,?,?,?,?)", filas_partido)
            con.executemany("INSERT INTO fact_actividad_ventana VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", filas_fact)
            con.executemany("INSERT INTO fact_estadistica_ventana VALUES (?,?,?,?,?,?,?,?,?,?)", filas_stats)
            destino = {
                "comentarios": con.execute("SELECT COALESCE(SUM(comentarios),0) FROM fact_actividad_ventana").fetchone()[0],
                "eventos": con.execute("SELECT COALESCE(SUM(eventos),0) FROM fact_actividad_ventana").fetchone()[0],
                "filas_fact": con.execute("SELECT COUNT(*) FROM fact_actividad_ventana").fetchone()[0],
                "partidos": con.execute("SELECT COUNT(*) FROM dim_partido").fetchone()[0],
                "equipos": con.execute("SELECT COUNT(*) FROM dim_equipo").fetchone()[0],
                "huerfanos": con.execute("SELECT COUNT(*) FROM fact_actividad_ventana f LEFT JOIN dim_partido p "
                                         "USING(partido_id) WHERE p.partido_id IS NULL").fetchone()[0],
                "duplicados": con.execute("SELECT COUNT(*) - COUNT(DISTINCT partido_id || '|' || ventana) "
                                          "FROM fact_actividad_ventana").fetchone()[0],
            }
            fuente = {"comentarios_cassandra": filas_cass, "eventos_neo4j": sum(len(p["eventos"]) for p in neo),
                      "partidos_neo4j": len(neo), "equipos_neo4j_o_mongo": len(equipos), "filas_influx": len(influx)}
            validaciones = {
                "comentarios_fuente_igual_destino": destino["comentarios"] == filas_cass,
                "eventos_fuente_igual_destino": destino["eventos"] == fuente["eventos_neo4j"],
                "una_fila_por_partido_y_ventana": destino["filas_fact"] == len(neo) * VENTANAS and destino["duplicados"] == 0,
                "sin_hechos_huerfanos": destino["huerfanos"] == 0,
            }
            observaciones = {
                "equipos_con_nombre_distinto_neo4j_vs_mongo": sum(f[3] for f in filas_equipo),
                "partidos_con_fecha_neo4j_distinta_al_dia_de_actividad": fechas_distintas,
                "filas_influx_con_equipo_no_conciliado": sum(1 for f in filas_stats if not f[3]),
            }
            if not all(validaciones.values()):
                raise RuntimeError(f"Validación fallida, no se publica el lote: {validaciones}")
            con.execute("INSERT INTO control_lotes VALUES (?,?,?,?,?,?,?,?)",
                        (lote, inicio, comun.ahora_iso(), "publicado", json.dumps(fuente), json.dumps(destino),
                         json.dumps({**validaciones, "observaciones": observaciones}), round(time.perf_counter() - t0, 2)))
    finally:
        con.close()

    resultado = {"lote_id": lote, "duracion_s": round(time.perf_counter() - t0, 2), "conteos_fuente": fuente,
                 "conteos_destino": destino, "validaciones": validaciones, "observaciones": observaciones,
                 "archivo": str(DB_PATH.relative_to(comun.HITO_DIR))}
    comun.escribir_json(comun.EVIDENCIA_DIR / "data_mart_construccion.json", resultado)
    print(f"Destino: {destino}")
    for k, v in validaciones.items():
        print(f"  [{'OK ' if v else 'FALLA'}] {k}")
    print(f"Observaciones de calidad: {observaciones}")
    print(f"Lote publicado en {resultado['duracion_s']} s -> {resultado['archivo']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
