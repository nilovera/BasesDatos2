"""COMPARACIÓN MEDIDA: responder la pregunta analítica desde las fuentes operacionales (vía API)
vs. desde la proyección del Data Mart (SQLite, modelo relacional dimensional).  Hito 12, RF12-RF14.

Pregunta: "Top 10 de ventanas de 10 minutos con más comentarios en todo el torneo, y qué eventos
ocurrieron en cada una" + "evolución por ventana del partido PAR-0001".

Camino A (operacional): por cada partido, 15 GET de comentarios (uno por bucket, paginando) + 1 GET de
          eventos, con 8 solicitudes en paralelo, y la agregación se hace en el cliente.
Camino B (Data Mart): una consulta SQL con JOIN sobre fact_actividad_ventana + dim_partido.
Se verifica que ambos caminos den EXACTAMENTE la misma respuesta (consistencia fuente vs. proyección).

Uso:  python consultar_data_mart.py      (con la API levantada y después de construir_data_mart.py)
"""
from __future__ import annotations

import asyncio
import sqlite3
import statistics
import sys
import time

import httpx

import comun
from construir_data_mart import DB_PATH, TIPOS_GOL, TIPOS_TARJETA, VENTANAS, bucket_de

SQL_TOP = """
SELECT f.partido_id, f.ventana, f.comentarios, f.likes, f.eventos, f.goles, f.tarjetas, p.fase, p.sede
FROM fact_actividad_ventana f JOIN dim_partido p USING (partido_id)
ORDER BY f.comentarios DESC, f.likes DESC, f.partido_id, f.ventana
LIMIT 10
"""
SQL_PARTIDO = """
SELECT ventana, comentarios, likes, eventos, goles, tarjetas FROM fact_actividad_ventana
WHERE partido_id = 'PAR-0001' ORDER BY ventana
"""


async def camino_operacional(base_url: str, partidos: list[str]) -> tuple[list, list, int]:
    llamadas = 0
    sem = asyncio.Semaphore(8)
    filas: dict[tuple, dict] = {}

    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        async def get(url):
            nonlocal llamadas
            async with sem:
                llamadas += 1
                r = await c.get(url)
                r.raise_for_status()
                return r.json()

        async def comentarios(p, v):
            bucket, _ = bucket_de(p, v)
            total = likes = 0
            url = f"/api/v1/partidos/{p}/comentarios?bucket_10min={bucket}&limit=100"
            while True:
                d = await get(url)
                total += len(d["datos"])
                likes += sum(x["likes"] or 0 for x in d["datos"])
                estado = d["paginacion"]
                if not estado.get("hay_mas"):
                    break
                url = (f"/api/v1/partidos/{p}/comentarios?bucket_10min={bucket}&limit=100"
                       f"&page_state={estado['siguiente_page_state']}")
            filas[(p, v)] = {"comentarios": total, "likes": likes, "tipos": []}

        async def eventos(p):
            d = await get(f"/api/v1/partidos/{p}/eventos")
            return p, d.get("eventos", [])

        await asyncio.gather(*(comentarios(p, v) for p in partidos for v in range(VENTANAS)))
        for p, evs in await asyncio.gather(*(eventos(p) for p in partidos)):
            for ev in evs:
                if ev.get("minuto") is not None:
                    filas[(p, min(int(ev["minuto"]) // 10, VENTANAS - 1))]["tipos"].append(ev["tipo"])

    def tupla(k, f):
        t = f["tipos"]
        return (k[0], k[1], f["comentarios"], f["likes"], len(t), sum(x in TIPOS_GOL for x in t), sum(x in TIPOS_TARJETA for x in t))
    todas = sorted((tupla(k, f) for k, f in filas.items()), key=lambda x: (-x[2], -x[3], x[0], x[1]))
    par1 = [tupla(k, f)[1:] for k, f in sorted(filas.items()) if k[0] == "PAR-0001"]
    return todas[:10], par1, llamadas


def main() -> int:
    cfg = comun.cargar_config()
    if not DB_PATH.exists():
        print("[ERROR] Falta el Data Mart: ejecutar antes construir_data_mart.py")
        return 1
    con = sqlite3.connect(DB_PATH)
    partidos = [r[0] for r in con.execute("SELECT partido_id FROM dim_partido ORDER BY partido_id")]
    lote = con.execute("SELECT lote_id, fin FROM control_lotes WHERE estado='publicado' ORDER BY fin DESC LIMIT 1").fetchone()
    print(f"=== HITO 12 - FUENTES OPERACIONALES vs DATA MART (lote {lote[0]}) ===")

    tiempos_b = []
    for _ in range(50):
        t = time.perf_counter()
        top_b = con.execute(SQL_TOP).fetchall()
        par_b = con.execute(SQL_PARTIDO).fetchall()
        tiempos_b.append((time.perf_counter() - t) * 1000)
    con.close()

    tiempos_a, llamadas = [], 0
    for i in range(3):
        t = time.perf_counter()
        top_a, par_a, llamadas = asyncio.run(camino_operacional(cfg["api_base_url"], partidos))
        tiempos_a.append((time.perf_counter() - t) * 1000)
        print(f"  camino operacional, repetición {i + 1}: {tiempos_a[-1]:.0f} ms, {llamadas} llamadas HTTP")

    top_b_cmp = [tuple(r[:7]) for r in top_b]
    par_b_cmp = [tuple(r) for r in par_b]
    iguales = top_a == top_b_cmp and par_a == par_b_cmp
    resultado = {
        "fecha": comun.ahora_iso(), "lote_data_mart": lote[0], "lote_publicado_en": lote[1],
        "operacional": {"llamadas_http": llamadas, "concurrencia": 8, "repeticiones": 3,
                        "ms_mediana": round(statistics.median(tiempos_a), 1), "ms_todas": [round(x, 1) for x in tiempos_a]},
        "data_mart": {"consultas_sql": 2, "repeticiones": 50, "ms_mediana": round(statistics.median(tiempos_b), 3),
                      "ms_p95": round(sorted(tiempos_b)[int(0.95 * 49)], 3)},
        "misma_respuesta": iguales,
        "top10": [dict(zip(["partido", "ventana", "comentarios", "likes", "eventos", "goles", "tarjetas", "fase", "sede"], r)) for r in top_b],
        "par0001_por_ventana": [dict(zip(["ventana", "comentarios", "likes", "eventos", "goles", "tarjetas"], r)) for r in par_b],
        "nota": "El Data Mart responde con datos del último lote publicado (retraso = antigüedad del lote).",
    }
    comun.escribir_json(comun.EVIDENCIA_DIR / "data_mart_comparacion.json", resultado)
    print(f"\nOperacional (API sobre Cassandra + Neo4j, {llamadas} llamadas): mediana {resultado['operacional']['ms_mediana']} ms")
    print(f"Data Mart (2 consultas SQL): mediana {resultado['data_mart']['ms_mediana']} ms | P95 {resultado['data_mart']['ms_p95']} ms")
    print(f"Misma respuesta en ambos caminos: {'SÍ' if iguales else 'NO'}")
    print("\nTop 10 ventanas por comentarios:")
    for r in top_b:
        print(f"  {r[0]} ventana {r[1]:>2} ({r[1]*10}-{r[1]*10+9}')  comentarios {r[2]:>3}  likes {r[3]:>4}  eventos {r[4]}")
    print("Evidencia: docs/evidencia/data_mart_comparacion.json")
    return 0 if iguales else 2


if __name__ == "__main__":
    sys.exit(main())
