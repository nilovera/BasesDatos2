"""Verifica que Prometheus esté recolectando cada componente y guarda la evidencia.

Consulta la API HTTP de Prometheus (no la interfaz web) y muestra, por target:
job, componente, capa, mecanismo, estado (UP/DOWN), último scraping y error.
Además resume tres vistas de disponibilidad de las bases:
  - fixture_dependencia_up  (la API puede usar la base)
  - probe_success sonda-tcp (el puerto acepta conexiones)
  - <exporter>_up           (el exporter llega al motor)

Guarda evidencia/prometheus_targets.json y evidencia/prometheus_targets.md.
Código de salida 0 si todos los jobs esperados están UP; 2 si alguno falta.

Uso: .venv\\Scripts\\python.exe fixture2030-hito-13-monitoreo\\scripts\\verificar_targets.py
"""
from __future__ import annotations

import sys

import httpx

import comun_monitoreo as cm


def valor(resultado: list[dict], etiqueta: str) -> dict[str, str]:
    return {r["metric"].get(etiqueta, "?"): r["value"][1] for r in resultado}


def main() -> int:
    if not cm.prom_disponible():
        print("[ERROR] Prometheus no responde en http://localhost:9090 (¿se ejecutó iniciar_monitoreo.ps1?)")
        return 1

    targets = httpx.get(f"{cm.PROMETHEUS}/api/v1/targets", params={"state": "active"}, timeout=15).json()
    filas = []
    for t in targets["data"]["activeTargets"]:
        lab = t["labels"]
        filas.append({
            "job": lab.get("job"),
            "componente": lab.get("componente", ""),
            "capa": lab.get("capa", ""),
            "mecanismo": lab.get("mecanismo", ""),
            "instance": lab.get("instance", ""),
            "estado": t["health"].upper(),
            "ultimo_scraping": t.get("lastScrape", "")[:19],
            "duracion_scraping_s": round(t.get("lastScrapeDuration", 0.0), 3),
            "error": (t.get("lastError") or "")[:160],
        })
    filas.sort(key=lambda f: (f["capa"], f["job"], f["componente"]))

    vistas = {
        "api_puede_usar_la_base (fixture_dependencia_up)": valor(cm.prom_query("max by (dependencia) (fixture_dependencia_up)"), "dependencia"),
        "puerto_acepta_conexiones (probe_success sonda-tcp)": valor(cm.prom_query('max by (componente) (probe_success{job="sonda-tcp"})'), "componente"),
        "exporter_llega_al_motor": {
            "MongoDB (mongodb_up)": next(iter(valor(cm.prom_query("max(mongodb_up)"), "x").values()), "sin dato"),
            "Redis (redis_up)": next(iter(valor(cm.prom_query("max(redis_up)"), "x").values()), "sin dato"),
        },
    }
    alertas = [
        {"alerta": r["metric"].get("alertname"), "estado": r["metric"].get("alertstate"),
         "severidad": r["metric"].get("severidad"), "objeto": r["metric"].get("dependencia") or r["metric"].get("componente") or r["metric"].get("job")}
        for r in cm.prom_query("ALERTS")
    ]
    reglas = httpx.get(f"{cm.PROMETHEUS}/api/v1/rules", timeout=15).json()["data"]["groups"]
    total_reglas = sum(len(g["rules"]) for g in reglas)

    jobs_up = {f["job"] for f in filas if f["estado"] == "UP"}
    jobs_con_down = {f["job"] for f in filas if f["estado"] != "UP"}
    faltan = [j for j in cm.JOBS_ESPERADOS if j not in jobs_up or j in jobs_con_down]

    # ------------------------------------------------------------ consola
    print(f"\n=== TARGETS DE PROMETHEUS ({cm.ahora_iso()}) ===")
    print(f"{'JOB':<14}{'COMPONENTE':<20}{'CAPA':<16}{'MECANISMO':<18}{'ESTADO':<8}ERROR")
    for f in filas:
        print(f"{f['job']:<14}{f['componente'][:19]:<20}{f['capa']:<16}{f['mecanismo']:<18}{f['estado']:<8}{f['error'][:70]}")
    print("\n=== DISPONIBILIDAD DE LAS BASES (tres capas) ===")
    for vista, datos in vistas.items():
        print(f"- {vista}: " + ", ".join(f"{k}={'OK' if v == '1' else ('CAÍDA' if v == '0' else v)}" for k, v in datos.items()))
    print(f"\nReglas cargadas: {total_reglas} | Alertas activas: {len([a for a in alertas if a['estado'] == 'firing'])}"
          f" | pendientes: {len([a for a in alertas if a['estado'] == 'pending'])}")
    for a in alertas:
        print(f"   [{a['estado']}] {a['alerta']} ({a['severidad']}) -> {a['objeto']}")
    if faltan:
        print(f"\n[AVISO] Jobs esperados que no están completamente UP: {', '.join(faltan)}")
        print("        Ver README -> 'Investigar un target DOWN'. cadvisor es opcional (perfil 'contenedores').")
    else:
        print("\nTodos los jobs esperados están UP.")

    # ------------------------------------------------------------ evidencia
    datos = {"fecha": cm.ahora_iso(), "commit": cm.commit_actual(), "targets": filas, "disponibilidad": vistas,
             "reglas_cargadas": total_reglas, "alertas": alertas, "jobs_esperados_no_up": faltan}
    cm.escribir_json(cm.EVIDENCIA_DIR / "prometheus_targets.json", datos)

    # Inventario de métricas que entrega cada job (qué se mide directamente y qué vía exporter).
    inventario = {}
    for job in sorted({f["job"] for f in filas if f["estado"] == "UP"}):
        nombres = cm.prom_query(f'count by (__name__) ({{job="{job}"}})')
        inventario[job] = {"series": int(sum(float(r["value"][1]) for r in nombres)),
                           "metricas": sorted(r["metric"]["__name__"] for r in nombres)}
    cm.escribir_json(cm.RESULTADOS_DIR / "metricas_disponibles.json",
                     {"fecha": datos["fecha"], "commit": datos["commit"], "por_job": inventario})
    print("Inventario de métricas por job: evidencia/resultados_sin_secretos/metricas_disponibles.json")

    md = [f"# Targets de Prometheus - {datos['fecha']}", "",
          f"Generado por `scripts/verificar_targets.py` sobre el commit `{datos['commit']}`. "
          "Fuente: `GET /api/v1/targets` y `GET /api/v1/query` de Prometheus.", "",
          "| Job | Componente | Capa | Mecanismo | Estado | Duración scraping (s) | Error |",
          "|---|---|---|---|---|---:|---|"]
    md += [f"| {f['job']} | {f['componente']} | {f['capa']} | {f['mecanismo']} | **{f['estado']}** | "
           f"{f['duracion_scraping_s']} | {f['error'].replace('|', '/') or '—'} |" for f in filas]
    md += ["", "## Disponibilidad de las bases en tres capas", ""]
    for vista, d in vistas.items():
        md.append(f"- **{vista}:** " + ", ".join(f"{k} = {v}" for k, v in d.items()))
    md += ["", f"Reglas cargadas: **{total_reglas}**. Alertas en este momento: "
           + (", ".join(f"{a['alerta']} [{a['estado']}] → {a['objeto']}" for a in alertas) or "ninguna") + "."]
    if faltan:
        md += ["", f"Jobs esperados que no estaban UP: {', '.join(faltan)}."]
    (cm.EVIDENCIA_DIR / "prometheus_targets.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\nEvidencia: evidencia/prometheus_targets.json y evidencia/prometheus_targets.md")
    return 2 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
