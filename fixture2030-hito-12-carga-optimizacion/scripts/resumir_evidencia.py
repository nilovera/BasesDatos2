"""RESÚMENES DE EVIDENCIA (punto 9 del enunciado: resultados_linea_base.*, resultados_optimizados.*,
tablas_o_graficos.*).

Lee las carpetas de corrida de docs/evidencia/ y genera, sin escribir ningún número a mano:
  - resultados_linea_base.md / .json   todas las corridas 'linea_base_*' (y la v1 descartada, aparte)
  - resultados_optimizados.md / .json  todas las corridas 'optimizada_*'
  - tablas_o_graficos.md               índice de tablas y gráficos (comparación, diagnóstico, Data Mart)

Uso:  python resumir_evidencia.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import comun

EV = comun.EVIDENCIA_DIR


def cargar(c: Path) -> dict:
    leer = lambda n: json.loads((c / n).read_text(encoding="utf-8")) if (c / n).exists() else None  # noqa: E731
    return {"nombre": c.name, "resumen": leer("resumen.json"), "meta": leer("metadatos.json"), "integ": leer("integridad.json"),
            "recursos": list(csv.DictReader((c / "recursos.csv").open(encoding="utf-8"))) if (c / "recursos.csv").exists() else []}


def rec_fase(filas: list[dict], fase: str, campo: str):
    v = []
    for f in filas:
        try:
            if f["fase"] == fase and float(f["t_s"]) >= 0 and f.get(campo) not in (None, ""):
                v.append(float(f[campo]))
        except ValueError:
            pass
    return round(sum(v) / len(v), 1) if v else None


def seccion(run: dict) -> list[str]:
    r, m, i = run["resumen"], run["meta"], run["integ"] or {}
    g = r["global_medido"]
    L = [f"## `{run['nombre']}`\n",
         "| Dato | Valor |\n|---|---|",
         f"| Inicio / fin | {m['inicio']} / {m.get('fin')} |",
         f"| Commit API (rama) | `{m['git']['commit']}` ({m['git']['rama']}), cambios sin commit en `app/`: {m['git']['codigo_api_modificado_sin_commit']} |",
         f"| IRIS_POOL_SIZE | {r.get('iris_pool_size')} |",
         f"| Escenario / generador | {m['escenario']} / {m['herramienta']} |",
         f"| Corte seguro | {m.get('corte')} |",
         f"| Hardware | {m['hardware'].get('procesador')}, {m['hardware'].get('nucleos_fisicos')}/{m['hardware'].get('procesadores_logicos')} núcleos, {m['hardware'].get('ram_total_gb')} GB |",
         f"| /health/ready previo | HTTP {m.get('health_ready_previo', {}).get('http')} |",
         f"| Global medido | {g['solicitudes']} solicitudes, {g['exitosas']} exitosas, error {g['tasa_error_pct']} %, "
         f"{g['throughput_ok_rps']} req/s, P50 {g['latencia_ms']['p50']} ms, P95 {g['latencia_ms']['p95']} ms, "
         f"P99 {g['latencia_ms']['p99']} ms, máx {g['latencia_ms']['max']} ms |",
         f"| Integridad | {'APROBADO' if i.get('aprobado') else 'sin validar' if not i else 'CON OBSERVACIONES'}"
         + (f" — generadas {i['conteos']['generadas']}, exitosas y correctas {i['conteos']['exitosas_y_correctas']}, "
            f"alteradas {i['integridad_contenido'].get('alterada', 0)}, duplicadas {i['request_id_duplicados']}" if i else "") + " |\n",
         "| Fase | Solicitudes | req/s | P50 | P95 | P99 | Máx | API P50 | API P95 | Errores | CPU API | CPU IRIS | CPU generador |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for fase, v in r["por_fase"].items():
        lm, am = v["latencia_ms"], v["api_ms"]
        L.append(f"| {fase} | {v['solicitudes']} | {v['throughput_ok_rps']} | {lm['p50']} | {lm['p95']} | {lm['p99']} | {lm['max']} | "
                 f"{am['p50']} | {am['p95']} | {v['fallidas']} | {rec_fase(run['recursos'], fase, 'api_cpu_pct')} | "
                 f"{rec_fase(run['recursos'], fase, 'iris_cpu_pct')} | {rec_fase(run['recursos'], fase, 'generador_cpu_pct')} |")
    if r.get("sostenimiento_por_operacion"):
        L += ["\nPor operación en el sostenimiento:\n",
              "| Operación | Solicitudes | P50 | P95 | P99 | API P50 | API P95 |", "|---|---:|---:|---:|---:|---:|---:|"]
        for o, v in r["sostenimiento_por_operacion"].items():
            lm, am = v["latencia_ms"], v["api_ms"]
            L.append(f"| {o} | {v['solicitudes']} | {lm['p50']} | {lm['p95']} | {lm['p99']} | {am['p50']} | {am['p95']} |")
    L.append("\nLatencias en ms (cliente). CPU: promedio de la fase, 100 % = 1 núcleo.\n")
    return L


def escribir(prefijo: str, titulo: str, nota: str, extra: list[Path] = ()) -> None:
    corridas = [cargar(c) for c in sorted(EV.glob(f"{prefijo}_2*")) if c.is_dir()]
    L = [f"# {titulo}\n", f"Generado por `scripts/resumir_evidencia.py` el {comun.ahora_iso()} a partir de las carpetas de corrida. "
         "Los datos crudos de cada corrida (una fila por solicitud) están en su carpeta.\n", nota + "\n"]
    for run in corridas:
        L += seccion(run)
    for c in extra:
        if c.is_dir():
            L += ["\n---\n", "### Corrida descartada como línea base (se conserva como evidencia)\n"]
            L += seccion(cargar(c))
    (EV / f"resultados_{'linea_base' if prefijo == 'linea_base' else 'optimizados'}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    comun.escribir_json(EV / f"resultados_{'linea_base' if prefijo == 'linea_base' else 'optimizados'}.json",
                        [{"corrida": r["nombre"], "commit": r["meta"]["git"]["commit"], "iris_pool_size": r["resumen"].get("iris_pool_size"),
                          "global_medido": r["resumen"]["global_medido"], "por_fase": r["resumen"]["por_fase"],
                          "sostenimiento_por_operacion": r["resumen"].get("sostenimiento_por_operacion"),
                          "integridad_aprobada": (r["integ"] or {}).get("aprobado")} for r in corridas])


def indice() -> None:
    L = ["# Tablas y gráficos del Hito 12\n", f"Índice generado por `scripts/resumir_evidencia.py` el {comun.ahora_iso()}.\n",
         "## 1. Comparación antes / después\n",
         "Tablas completas (global, por fase, por operación, recursos, integridad y repeticiones): "
         "[`comparacion/comparacion.md`](comparacion/comparacion.md) · datos: [`comparacion/comparacion.json`](comparacion/comparacion.json)\n"]
    titulos = {"01": "Latencia P95 en el tiempo (todas las operaciones)", "02": "Throughput en el tiempo",
               "03": "Latencia P95 del endpoint de IRIS en el tiempo", "04": "P95 por operación durante el sostenimiento",
               "05": "CPU de la API y del contenedor IRIS"}
    for png in sorted((EV / "comparacion").glob("*.png")):
        L += [f"### {titulos.get(png.name[:2], png.stem)}\n", f"![{png.stem}](comparacion/{png.name})\n"]
    d = EV / "diagnostico_iris.json"
    if d.exists():
        dj = json.loads(d.read_text(encoding="utf-8"))
        L += ["## 2. Diagnóstico de la hipótesis (directo contra IRIS)\n",
              "| Escenario | Hilos | ops/s | connect() ms | consulta ms | P50 ms | P95 ms | Errores |", "|---|---:|---:|---:|---:|---:|---:|---|"]
        for x in dj["resultados"]:
            L.append(f"| {x['escenario']} | {x.get('hilos')} | {x.get('ops_por_s')} | {x.get('connect_ms_prom')} | {x.get('consulta_ms_prom')} | "
                     f"{x.get('total_ms_p50')} | {x.get('total_ms_p95')} | {x.get('errores') or '-'} |")
        lic = dj.get("licencias") or {}
        L.append(f"\nConexiones simultáneas aceptadas por IRIS Community: **{lic.get('conexiones_simultaneas_aceptadas')}** "
                 f"(rechazo: {lic.get('rechazo')}). Fuente: [`diagnostico_iris.json`](diagnostico_iris.json)\n")
    c, k = EV / "data_mart_construccion.json", EV / "data_mart_comparacion.json"
    if c.exists() and k.exists():
        cj, kj = json.loads(c.read_text(encoding="utf-8")), json.loads(k.read_text(encoding="utf-8"))
        L += ["## 3. Data Mart\n", "| Conteo | Fuente | Destino |", "|---|---:|---:|",
              f"| Comentarios | {cj['conteos_fuente']['comentarios_cassandra']} | {cj['conteos_destino']['comentarios']} |",
              f"| Eventos | {cj['conteos_fuente']['eventos_neo4j']} | {cj['conteos_destino']['eventos']} |",
              f"| Partidos | {cj['conteos_fuente']['partidos_neo4j']} | {cj['conteos_destino']['partidos']} |",
              f"\nValidaciones: {cj['validaciones']} · Observaciones de calidad: {cj['observaciones']}\n",
              "| Camino | Operaciones | Tiempo (mediana) |", "|---|---:|---:|",
              f"| Fuentes operacionales vía API | {kj['operacional']['llamadas_http']} llamadas HTTP | {kj['operacional']['ms_mediana']} ms |",
              f"| Data Mart (SQLite) | {kj['data_mart']['consultas_sql']} consultas SQL | {kj['data_mart']['ms_mediana']} ms |",
              f"\nMisma respuesta en ambos caminos: **{'sí' if kj['misma_respuesta'] else 'no'}**. Fuentes: "
              "[`data_mart_construccion.json`](data_mart_construccion.json), [`data_mart_comparacion.json`](data_mart_comparacion.json)\n"]
    L += ["## 4. Resultados por corrida\n", "- [`resultados_linea_base.md`](resultados_linea_base.md)",
          "- [`resultados_optimizados.md`](resultados_optimizados.md)", "- Capturas de consola: [`capturas_redactadas/`](capturas_redactadas/)\n"]
    (EV / "tablas_o_graficos.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    escribir("linea_base", "Resultados de la línea base",
             "Configuración: API sin pool de IRIS (`IRIS_POOL_SIZE=0`). Escenario `completo` con el generador de 4 procesos.",
             extra=sorted(EV.glob("v1_linea_base_*")))
    escribir("optimizada", "Resultados de la versión optimizada",
             "Configuración: API con pool de IRIS (`IRIS_POOL_SIZE=5`, commit `542a1d8`). Mismo escenario, datos y semilla que la línea base.")
    indice()
    print("Generados: resultados_linea_base.md/.json, resultados_optimizados.md/.json, tablas_o_graficos.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
