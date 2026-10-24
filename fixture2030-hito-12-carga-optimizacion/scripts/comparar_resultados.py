"""COMPARACIÓN antes / después (Hito 12, RF10).

Toma la última corrida 'linea_base_*' y la última 'optimizada_*' (o las que se indiquen) y genera
en docs/evidencia/comparacion/:
  - comparacion.md   tablas de latencia, percentiles, throughput, errores, recursos e integridad
  - comparacion.json los mismos números en formato estructurado
  - 4 gráficos PNG (latencia P95 y throughput en el tiempo, P95 por operación, CPU API/IRIS)

Uso:  python comparar_resultados.py [carpeta_linea_base] [carpeta_optimizada]
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import comun

SALIDA = comun.EVIDENCIA_DIR / "comparacion"


def ubicar(prefijo: str, arg: str | None) -> Path:
    if arg:
        return comun.EVIDENCIA_DIR / arg
    c = sorted(p for p in comun.EVIDENCIA_DIR.glob(f"{prefijo}_2*") if p.is_dir())
    if not c:
        raise SystemExit(f"[ERROR] No hay corridas '{prefijo}_*'")
    return c[-1]


def leer_csv(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def recursos_por_fase(filas: list[dict]) -> dict:
    """Promedios por fase desde recursos.csv, ignorando muestras previas al inicio (t<0)."""
    campos = ["api_cpu_pct", "api_ram_mb", "iris_cpu_pct", "cassandra_cpu_pct", "influxdb_cpu_pct",
              "generador_cpu_pct", "sistema_cpu_pct", "sistema_ram_pct", "lag_loop_max_ms"]
    out: dict = {}
    for f in filas:
        if (num(f["t_s"]) or 0) < 0 or f["fase"] in ("espera", "fin"):
            continue
        d = out.setdefault(f["fase"], {c: [] for c in campos})
        for c in campos:
            v = num(f.get(c))
            if v is not None:
                d[c].append(v)
    return {fase: {c: round(sum(v) / len(v), 1) if v else None for c, v in d.items()} for fase, d in out.items()}


def delta(a, b) -> str:
    if a in (None, 0) or b is None:
        return "-"
    return f"{(b - a) / a * 100:+.1f}%"


def cargar(corrida: Path) -> dict:
    return {
        "nombre": corrida.name,
        "resumen": json.loads((corrida / "resumen.json").read_text(encoding="utf-8")),
        "metadatos": json.loads((corrida / "metadatos.json").read_text(encoding="utf-8")),
        "integridad": json.loads((corrida / "integridad.json").read_text(encoding="utf-8"))
        if (corrida / "integridad.json").exists() else None,
        "serie": leer_csv(corrida / "serie_tiempo.csv"),
        "recursos": leer_csv(corrida / "recursos.csv"),
    }


def graficos(a: dict, b: dict) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[AVISO] matplotlib no instalado: se omiten los gráficos")
        return []
    colores = {"antes": "#c0504d", "despues": "#2e75b6"}
    etiquetas = {"antes": f"Línea base (sin pool)", "despues": f"Optimizada (pool IRIS)"}
    hechos = []

    def serie(run, campo):
        xs = [num(f["t_s"]) for f in run["serie"] if num(f.get(campo)) is not None]
        ys = [num(f[campo]) for f in run["serie"] if num(f.get(campo)) is not None]
        return xs, ys

    def fondo_fases(ax):
        acumulado = 0
        for i, f in enumerate(a["metadatos"]["config_prueba"]["fases"]):
            if i % 2 == 0:
                ax.axvspan(acumulado, acumulado + f["duracion_s"], color="#f2f2f2", zorder=0)
            ax.text(acumulado + 2, 0.98, f["nombre"], transform=ax.get_xaxis_transform(), fontsize=7, va="top", color="#666")
            acumulado += f["duracion_s"]

    for nombre, campo, titulo, ylab in [
        ("01_latencia_p95_en_el_tiempo.png", "p95_ms", "Latencia P95 vista por el cliente (ventanas de 5 s)", "ms"),
        ("02_throughput_en_el_tiempo.png", "rps_ok", "Solicitudes exitosas por segundo (ventanas de 5 s)", "req/s"),
        ("03_iris_p95_en_el_tiempo.png", "iris_p95_ms", "Latencia P95 del endpoint de IRIS (ventanas de 5 s)", "ms"),
    ]:
        fig, ax = plt.subplots(figsize=(10, 4.2))
        fondo_fases(ax)
        for k, run in (("antes", a), ("despues", b)):
            xs, ys = serie(run, campo)
            ax.plot(xs, ys, color=colores[k], label=etiquetas[k], linewidth=1.6)
        ax.set_title(titulo)
        ax.set_xlabel("segundos desde el inicio")
        ax.set_ylabel(ylab)
        ax.legend(loc="upper left")
        ax.grid(alpha=.3)
        fig.tight_layout()
        fig.savefig(SALIDA / nombre, dpi=120)
        plt.close(fig)
        hechos.append(nombre)

    ops = list(a["resumen"]["sostenimiento_por_operacion"].keys())
    fig, ax = plt.subplots(figsize=(10, 4.2))
    x = range(len(ops))
    for desplaz, (k, run) in zip((-0.2, 0.2), (("antes", a), ("despues", b))):
        vals = [run["resumen"]["sostenimiento_por_operacion"][o]["latencia_ms"]["p95"] or 0 for o in ops]
        ax.bar([i + desplaz for i in x], vals, width=0.4, color=colores[k], label=etiquetas[k])
    ax.set_xticks(list(x))
    ax.set_xticklabels([o.replace("_", "\n") for o in ops], fontsize=8)
    ax.set_title("Latencia P95 por operación durante el sostenimiento (40 VUs)")
    ax.set_ylabel("ms")
    ax.legend()
    ax.grid(axis="y", alpha=.3)
    fig.tight_layout()
    fig.savefig(SALIDA / "04_p95_por_operacion.png", dpi=120)
    plt.close(fig)
    hechos.append("04_p95_por_operacion.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for ax, campo, titulo in zip(axes, ("api_cpu_pct", "iris_cpu_pct"), ("CPU del proceso de la API", "CPU del contenedor IRIS")):
        for k, run in (("antes", a), ("despues", b)):
            filas = [f for f in run["recursos"] if (num(f["t_s"]) or -1) >= 0 and num(f.get(campo)) is not None]
            ax.plot([num(f["t_s"]) for f in filas], [num(f[campo]) for f in filas], color=colores[k], label=etiquetas[k])
        ax.set_title(f"{titulo} (100% = 1 núcleo)")
        ax.set_xlabel("segundos")
        ax.grid(alpha=.3)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(SALIDA / "05_cpu_api_e_iris.png", dpi=120)
    plt.close(fig)
    hechos.append("05_cpu_api_e_iris.png")
    return hechos


def main() -> int:
    a = cargar(ubicar("linea_base", sys.argv[1] if len(sys.argv) > 1 else None))
    b = cargar(ubicar("optimizada", sys.argv[2] if len(sys.argv) > 2 else None))
    SALIDA.mkdir(parents=True, exist_ok=True)
    ra, rb = a["resumen"], b["resumen"]
    reca, recb = recursos_por_fase(a["recursos"]), recursos_por_fase(b["recursos"])

    ma, mb = a["metadatos"], b["metadatos"]
    mismas = {
        "escenario": ma["escenario"] == mb["escenario"],
        "fases": ma["config_prueba"]["fases"] == mb["config_prueba"]["fases"],
        "mezcla": ma["config_prueba"]["mezcla_operaciones"] == mb["config_prueba"]["mezcla_operaciones"],
        "semilla": ma["config_prueba"]["semilla"] == mb["config_prueba"]["semilla"],
        "procesos_generador": ma["config_prueba"].get("procesos_generador") == mb["config_prueba"].get("procesos_generador"),
        "catalogo_claves": ma["catalogo"].get("total_claves") == mb["catalogo"].get("total_claves"),
    }

    L = []
    L.append("# Comparación línea base vs. optimizada\n")
    L.append(f"Generado por `scripts/comparar_resultados.py` el {comun.ahora_iso()}.\n")
    L.append("| | Línea base | Optimizada |\n|---|---|---|")
    L.append(f"| Corrida | `{a['nombre']}` | `{b['nombre']}` |")
    L.append(f"| Commit API | `{ma['git']['commit']}` (modificado sin commit: {ma['git']['codigo_api_modificado_sin_commit']}) | `{mb['git']['commit']}` (modificado sin commit: {mb['git']['codigo_api_modificado_sin_commit']}) |")
    L.append(f"| IRIS_POOL_SIZE | {ra.get('iris_pool_size')} | {rb.get('iris_pool_size')} |")
    L.append(f"| Inicio | {ma['inicio']} | {mb['inicio']} |")
    L.append(f"| Corte seguro | {ma.get('corte')} | {mb.get('corte')} |\n")
    L.append("**Condiciones equivalentes:** " + ", ".join(f"{k} {'✔' if v else '✘'}" for k, v in mismas.items()) + "\n")

    def fila_global(nombre, f):
        va, vb = f(ra["global_medido"]), f(rb["global_medido"])
        return f"| {nombre} | {va} | {vb} | {delta(va, vb)} |"
    L.append("## 1. Resultado global (fases medidas: rampa + sostenimiento + pico + recuperación)\n")
    L.append("| Métrica | Línea base | Optimizada | Variación |\n|---|---:|---:|---:|")
    for n, f in [("Solicitudes", lambda g: g["solicitudes"]), ("Exitosas", lambda g: g["exitosas"]),
                 ("Tasa de error %", lambda g: g["tasa_error_pct"]), ("Throughput (req/s)", lambda g: g["throughput_ok_rps"]),
                 ("Latencia P50 (ms)", lambda g: g["latencia_ms"]["p50"]), ("Latencia P95 (ms)", lambda g: g["latencia_ms"]["p95"]),
                 ("Latencia P99 (ms)", lambda g: g["latencia_ms"]["p99"]), ("Latencia máx (ms)", lambda g: g["latencia_ms"]["max"]),
                 ("Tiempo en API P50 (ms)", lambda g: g["api_ms"]["p50"]), ("Tiempo en API P95 (ms)", lambda g: g["api_ms"]["p95"])]:
        L.append(fila_global(n, f))

    L.append("\n## 2. Por fase\n")
    L.append("| Fase | VUs | req/s antes | req/s después | P95 antes | P95 después | Var. P95 | P99 antes | P99 después | errores antes/después |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for f in ma["config_prueba"]["fases"]:
        n = f["nombre"]
        x, y = ra["por_fase"].get(n), rb["por_fase"].get(n)
        if not x or not y:
            continue
        L.append(f"| {n} | {f['vus_inicio']}→{f['vus_fin']} | {x['throughput_ok_rps']} | {y['throughput_ok_rps']} | "
                 f"{x['latencia_ms']['p95']} | {y['latencia_ms']['p95']} | {delta(x['latencia_ms']['p95'], y['latencia_ms']['p95'])} | "
                 f"{x['latencia_ms']['p99']} | {y['latencia_ms']['p99']} | {x['fallidas']} / {y['fallidas']} |")

    L.append("\n## 3. Por operación durante el sostenimiento (40 VUs, 180 s)\n")
    L.append("| Operación | P50 antes | P50 después | P95 antes | P95 después | Var. P95 | API P50 antes | API P50 después | Var. API P50 |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for o, x in ra["sostenimiento_por_operacion"].items():
        y = rb["sostenimiento_por_operacion"][o]
        L.append(f"| {o} | {x['latencia_ms']['p50']} | {y['latencia_ms']['p50']} | {x['latencia_ms']['p95']} | {y['latencia_ms']['p95']} | "
                 f"{delta(x['latencia_ms']['p95'], y['latencia_ms']['p95'])} | {x['api_ms']['p50']} | {y['api_ms']['p50']} | {delta(x['api_ms']['p50'], y['api_ms']['p50'])} |")

    L.append("\n## 4. Recursos (promedio por fase, muestreo cada 2 s; CPU 100% = 1 núcleo)\n")
    L.append("| Fase | CPU API antes | CPU API después | CPU IRIS antes | CPU IRIS después | CPU generador antes | CPU generador después | RAM sistema % antes/después | lag loop máx ms antes/después |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---|---|")
    for f in ma["config_prueba"]["fases"]:
        n = f["nombre"]
        x, y = reca.get(n), recb.get(n)
        if not x or not y:
            continue
        L.append(f"| {n} | {x['api_cpu_pct']} | {y['api_cpu_pct']} | {x['iris_cpu_pct']} | {y['iris_cpu_pct']} | "
                 f"{x['generador_cpu_pct']} | {y['generador_cpu_pct']} | {x['sistema_ram_pct']} / {y['sistema_ram_pct']} | {x['lag_loop_max_ms']} / {y['lag_loop_max_ms']} |")

    L.append("\n## 5. Integridad\n")
    L.append("| Chequeo | Línea base | Optimizada |\n|---|---|---|")
    ia, ib = a["integridad"] or {}, b["integridad"] or {}
    for k in (ia.get("chequeos") or {}):
        L.append(f"| {k} | {'OK' if ia['chequeos'][k] else 'FALLA'} | {'OK' if (ib.get('chequeos') or {}).get(k) else 'FALLA'} |")
    if ia and ib:
        L.append(f"| solicitudes generadas / exitosas y correctas | {ia['conteos']['generadas']} / {ia['conteos']['exitosas_y_correctas']} | "
                 f"{ib['conteos']['generadas']} / {ib['conteos']['exitosas_y_correctas']} |")

    hechos = graficos(a, b)
    if hechos:
        L.append("\n## 6. Gráficos\n")
        for h in hechos:
            L.append(f"![{h}]({h})\n")

    (SALIDA / "comparacion.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    comun.escribir_json(SALIDA / "comparacion.json", {
        "linea_base": a["nombre"], "optimizada": b["nombre"], "condiciones_equivalentes": mismas,
        "global": {"linea_base": ra["global_medido"], "optimizada": rb["global_medido"]},
        "por_fase": {"linea_base": ra["por_fase"], "optimizada": rb["por_fase"]},
        "sostenimiento_por_operacion": {"linea_base": ra["sostenimiento_por_operacion"], "optimizada": rb["sostenimiento_por_operacion"]},
        "recursos_por_fase": {"linea_base": reca, "optimizada": recb},
    })
    print("\n".join(L[:40]))
    print(f"\nComparación completa: docs/evidencia/comparacion/comparacion.md ({len(hechos)} gráficos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
