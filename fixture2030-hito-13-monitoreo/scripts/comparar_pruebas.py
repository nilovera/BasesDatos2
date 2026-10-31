"""Compara las corridas de la prueba controlada (sin corte rápido, corte v1 y corte v2).

Lee evidencia/prueba_de_falla_redis_corte*/ (resumen.json, linea_de_tiempo.json y
prometheus_series.json) y genera:
  - evidencia/comparacion_corte_rapido.md   tabla antes/después con la variación
  - evidencia/comparacion_corte_rapido.png  throughput total y P95 de Redis en el tiempo

No consulta Prometheus ni la API: trabaja solo con la evidencia ya guardada, así que se
puede regenerar en cualquier máquina.

Uso: .venv\\Scripts\\python.exe fixture2030-hito-13-monitoreo\\scripts\\comparar_pruebas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EVIDENCIA = Path(__file__).resolve().parents[1] / "evidencia"
NOMBRES = {"corte0": "Sin corte rápido", "corte10v1": "Corte rápido v1", "corte10v2": "Corte rápido v2 (adoptado)"}


def cargar() -> list[dict]:
    corridas = []
    for carpeta in sorted(EVIDENCIA.glob("prueba_de_falla_redis_corte*_*")):
        if not carpeta.is_dir():
            continue
        clave = carpeta.name.split("_")[4]
        corridas.append({
            "clave": clave, "nombre": NOMBRES.get(clave, clave), "carpeta": carpeta.name,
            "resumen": json.loads((carpeta / "resumen.json").read_text(encoding="utf-8")),
            "linea": json.loads((carpeta / "linea_de_tiempo.json").read_text(encoding="utf-8")),
            "series": json.loads((carpeta / "prometheus_series.json").read_text(encoding="utf-8")),
        })
    orden = list(NOMBRES)
    corridas.sort(key=lambda c: orden.index(c["clave"]) if c["clave"] in orden else 99)
    return corridas


def max_en_falla(c: dict, clave: str, dependencia: str | None) -> float | None:
    s = c["series"]
    t0 = s["desde"] + 60
    ini, fin = t0 + c["linea"]["stop_fin_s"], t0 + c["linea"]["start_inicio_s"]
    valores = [float(v) for serie in s["series"].get(clave, [])
               if dependencia is None or serie["metric"].get("dependencia") == dependencia
               for ts, v in serie["values"] if ini <= float(ts) <= fin and v not in ("NaN", "+Inf")]
    return max(valores) if valores else None


def var(a, b) -> str:
    if a in (None, 0) or b is None:
        return "—"
    return f"{100 * (b - a) / a:+.0f} %"


def main() -> int:
    corridas = cargar()
    if not corridas:
        print("No hay corridas en evidencia/")
        return 1
    filas = []
    for c in corridas:
        tr = c["resumen"]["cliente_por_tramo"]
        p95_redis = max_en_falla(c, "p95_por_base", "Redis")
        filas.append({
            "nombre": c["nombre"], "carpeta": c["carpeta"], "commit": c["resumen"]["commit"],
            "rps_antes": tr["antes"]["rps"], "rps_falla": tr["falla"]["rps"], "rps_despues": tr["despues"]["rps"],
            "p95_otras_falla": max(v["p95_ms"] or 0 for k, v in tr["falla"]["por_base"].items() if k != "Redis"),
            "p95_redis_max_ms": None if p95_redis is None else round(p95_redis * 1000, 1),
            "errores_5xx_otras": c["resumen"]["aislamiento"]["errores_5xx_en_las_otras_bases"],
            "errores_5xx_redis": c["resumen"]["aislamiento"]["errores_5xx_en_la_base_detenida"],
            "solicitudes_falla": tr["falla"]["solicitudes"],
            "deteccion_api_s": c["linea"].get("deteccion_desde_stop_api_s"),
            "deteccion_sonda_s": c["linea"].get("deteccion_desde_stop_sonda_s"),
            "recuperacion_api_s": c["linea"].get("recuperacion_vista_por_la_api_s"),
        })
    base = filas[0]
    md = ["# Comparación: falla de Redis sin y con corte rápido", "",
          "Generado por `scripts/comparar_pruebas.py` a partir de las carpetas `prueba_de_falla_redis_corte*`. "
          "Mismo escenario en las tres corridas: 20 usuarios virtuales constantes, mezcla del Hito 12, 60 s normales, "
          "Redis detenido 120 s (`docker stop`) y 90 s de recuperación, misma notebook y mismos datos. "
          "Una corrida por versión (ver limitaciones).", "",
          "| Métrica (medida) | " + " | ".join(f["nombre"] for f in filas) + " |",
          "|---|" + "---:|" * len(filas)]
    def fila(titulo, clave, sufijo="", comparar=True):
        celdas = []
        for f in filas:
            txt = "—" if f[clave] is None else f"{f[clave]}{sufijo}"
            if comparar and f is not base and isinstance(f[clave], (int, float)):
                txt += f" ({var(base[clave], f[clave])})"
            celdas.append(txt)
        md.append(f"| {titulo} | " + " | ".join(celdas) + " |")
    fila("Throughput total ANTES de la falla (req/s)", "rps_antes")
    fila("**Throughput total DURANTE la falla (req/s)**", "rps_falla")
    fila("Throughput total DESPUÉS de la falla (req/s)", "rps_despues")
    fila("Solicitudes atendidas durante los 120 s de falla", "solicitudes_falla")
    fila("**P95 máximo de las rutas de Redis durante la falla (ms, Prometheus)**", "p95_redis_max_ms")
    fila("P95 de las otras 5 bases durante la falla (ms, cliente, peor base)", "p95_otras_falla", comparar=False)
    fila("Errores 5xx en Redis (esperados: la base está caída)", "errores_5xx_redis", comparar=False)
    fila("Errores 5xx en las otras 5 bases", "errores_5xx_otras", comparar=False)
    fila("Detección por la sonda TCP (s desde el stop)", "deteccion_sonda_s", comparar=False)
    fila("Detección por la API (s desde el stop)", "deteccion_api_s", comparar=False)
    fila("Recuperación vista por la API (s desde el start)", "recuperacion_api_s", comparar=False)
    md += ["", "Commits de cada corrida: " + "; ".join(f"{f['nombre']} → `{f['commit']}`" for f in filas) + ".", "",
           "Carpetas: " + ", ".join(f"[`{f['carpeta']}`]({f['carpeta']}/)" for f in filas) + ".", "",
           "![Comparación](comparacion_corte_rapido.png)", ""]
    (EVIDENCIA / "comparacion_corte_rapido.md").write_text("\n".join(md), encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for c in corridas:
        s = c["series"]
        t0 = s["desde"] + 60
        total: dict[float, float] = {}
        for serie in s["series"]["rps_por_base"]:
            for ts, v in serie["values"]:
                total[float(ts)] = total.get(float(ts), 0.0) + float(v)
        xs = sorted(total)
        ax1.plot([x - t0 for x in xs], [total[x] for x in xs], label=c["nombre"], linewidth=2)
        for serie in s["series"]["p95_por_base"]:
            if serie["metric"].get("dependencia") == "Redis":
                ax2.plot([float(ts) - t0 for ts, _ in serie["values"]],
                         [float(v) * 1000 if v != "NaN" else float("nan") for _, v in serie["values"]],
                         label=c["nombre"], linewidth=2)
    linea = corridas[0]["linea"]
    for ax in (ax1, ax2):
        ax.axvspan(linea["stop_inicio_s"], linea["start_inicio_s"], color="red", alpha=0.08, label="Redis detenido")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    ax1.set_title("Throughput total de la API: sum(rate(fixture_http_requests_total[1m]))")
    ax1.set_ylabel("solicitudes/s")
    ax2.set_title("P95 de las rutas de Redis (histograma de la API, ventana 1 min)")
    ax2.set_ylabel("ms")
    ax2.set_xlabel("segundos desde el inicio de cada prueba")
    fig.tight_layout()
    fig.savefig(EVIDENCIA / "comparacion_corte_rapido.png", dpi=110)
    print("\n".join(md[:20]))
    print("\nGenerado: evidencia/comparacion_corte_rapido.md y .png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
