"""PRUEBA CONTROLADA del Hito 13: carga + falla de una base + recuperación, observada con Prometheus.

Línea de tiempo (valores por defecto):

    0 s ............ 60 s ................................ 180 s ..................... 270 s
    | tráfico normal | docker stop <base> (falla controlada) | docker start (recuperación) | fin
    + 45 s de espera final para que Prometheus registre el último tramo y evalúe las alertas.

El tráfico es la MISMA mezcla de operaciones del Hito 12 ("consulta del partido en vivo": Cassandra 30 %,
InfluxDB 20 %, Redis 15 %, Neo4j 15 %, IRIS 10 %, MongoDB 10 %) sobre las claves del catálogo del
Hito 12, con usuarios virtuales constantes. Solo hace lecturas (GET): no modifica datos (RNF5).

La falla es NO destructiva (RNF11): `docker stop` y `docker start` del contenedor de laboratorio; no se
borran volúmenes. Si la prueba se interrumpe, el script vuelve a iniciar el contenedor.

Evidencia (sin secretos) en evidencia/prueba_de_falla_<base>_<fecha>/ y resumen en evidencia/prueba_de_falla.md:
  - linea_de_tiempo.json      momentos exactos (stop, start, detección, alertas, recuperación)
  - resumen.json              métricas del cliente y de Prometheus por tramo
  - solicitudes_por_segundo.csv  conteo por segundo, tipo y código (lado cliente)
  - prometheus_series.json    series consultadas a Prometheus en la ventana de la prueba
  - salud_dependencias.json   /health/dependencias antes, durante y después
  - prueba_controlada.png     gráfico de 4 paneles con la falla marcada

Uso (desde la carpeta de la API, con la API y el monitoreo levantados):
    .venv\\Scripts\\python.exe fixture2030-hito-13-monitoreo\\scripts\\ejecutar_prueba_controlada.py --producto redis
    ... --producto ninguno --usuarios 40 --normal 180      (solo carga, sin falla)
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import random
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import httpx

import comun_monitoreo as cm

HITO12 = cm.API_ROOT / "fixture2030-hito-12-carga-optimizacion"
CATALOGO = HITO12 / "datos-o-generadores" / "catalogo_claves.json"
CONFIG_H12 = HITO12 / "config" / "configuracion-ejemplo.json"

TIPO_A_BASE = {
    "equipo_mongodb": "MongoDB", "eventos_neo4j": "Neo4j", "comentarios_cassandra": "Cassandra",
    "sesion_redis": "Redis", "estadisticas_influxdb": "InfluxDB", "detalle_iris": "InterSystems IRIS",
}


# ------------------------------------------------------------------ utilidades
def percentil(valores: list[float], p: float) -> float | None:
    if not valores:
        return None
    v = sorted(valores)
    k = (len(v) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return round(v[int(k)] if f == c else v[f] + (v[c] - v[f]) * (k - f), 2)


def docker(*args: str, timeout: float = 60) -> tuple[int, str]:
    r = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()


def contenedor_corriendo(nombre: str) -> bool:
    codigo, salida = docker("inspect", "-f", "{{.State.Running}}", nombre, timeout=20)
    return codigo == 0 and salida.strip() == "true"


def salud(refrescar: bool = True) -> dict:
    """/health/dependencias reducido a lo necesario (sin mensajes de drivers)."""
    try:
        r = httpx.get(f"{cm.API}/health/dependencias", params={"refrescar": str(refrescar).lower()}, timeout=20)
        cuerpo = r.json()
        return {
            "momento": cm.ahora_iso(), "http": r.status_code, "estado_general": cuerpo.get("estado_general"),
            "dependencias": {d["dependencia"]: {"estado": d["estado"], "clasificacion": d["clasificacion"],
                                                "duracion_ms": d["duracion_ms"]} for d in cuerpo.get("dependencias", [])},
        }
    except Exception as error:  # noqa: BLE001
        return {"momento": cm.ahora_iso(), "error": type(error).__name__}


def refrescar_sesiones_redis() -> str:
    """Vuelve a crear las sesiones sintéticas SES-H12-* del Hito 12 (vencen a las 4 h). Solo escribe en Redis."""
    sys.path.insert(0, str(HITO12 / "scripts"))
    try:
        import preparar_datos  # noqa: WPS433  (script del Hito 12)
        total = preparar_datos.preparar_redis()
        return f"{total} sesiones SES-H12-* presentes"
    except Exception as error:  # noqa: BLE001
        return f"no se pudieron refrescar ({type(error).__name__}); las rutas de sesión pueden responder 404"
    finally:
        sys.path.pop(0)


# ------------------------------------------------------------------ carga
class Generador:
    def __init__(self, usuarios: int, semilla: int) -> None:
        cfg = json.loads(CONFIG_H12.read_text(encoding="utf-8"))
        catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))["claves"]
        self.mezcla = cfg["mezcla_operaciones"]
        self.think = cfg["think_time_ms"]
        self.p_caliente = cfg["probabilidad_clave_caliente"]
        self.claves: dict[str, list[str]] = defaultdict(list)
        self.calientes: dict[str, list[str]] = defaultdict(list)
        for e in catalogo:
            self.claves[e["tipo"]].append(e["url"])
            if e.get("partido") == cfg["partido_caliente"] or e["clave"] == cfg["equipo_caliente"]:
                self.calientes[e["tipo"]].append(e["url"])
        self.usuarios = usuarios
        self.rng = random.Random(semilla)
        self.filas: list[tuple[float, str, int, float]] = []   # (t_epoch, tipo, codigo, latencia_ms)
        self.fin = 0.0

    def elegir(self) -> tuple[str, str]:
        tipo = self.rng.choices(list(self.mezcla), weights=list(self.mezcla.values()))[0]
        lista = self.calientes[tipo] if self.calientes[tipo] and self.rng.random() < self.p_caliente else self.claves[tipo]
        return tipo, self.rng.choice(lista)

    async def usuario(self, cliente: httpx.AsyncClient) -> None:
        while time.time() < self.fin:
            tipo, url = self.elegir()
            inicio = time.perf_counter()
            try:
                r = await cliente.get(url)
                codigo = r.status_code
            except httpx.TimeoutException:
                codigo = 0          # 0 = sin respuesta dentro del timeout del cliente
            except httpx.HTTPError:
                codigo = -1         # -1 = error de conexión con la API
            self.filas.append((time.time(), tipo, codigo, (time.perf_counter() - inicio) * 1000))
            await asyncio.sleep(self.rng.uniform(*self.think) / 1000)

    async def correr(self, duracion: float) -> None:
        self.fin = time.time() + duracion
        limites = httpx.Limits(max_connections=self.usuarios, max_keepalive_connections=self.usuarios)
        async with httpx.AsyncClient(base_url=cm.API, timeout=10, limits=limites) as cliente:
            await asyncio.gather(*(self.usuario(cliente) for _ in range(self.usuarios)))


# ------------------------------------------------------------------ orquestación
async def orquestar(args, contenedor: str | None, base: str | None, eventos: dict, salud_registro: dict) -> None:
    await asyncio.sleep(args.normal)
    if not contenedor:
        return
    eventos["stop_inicio"] = time.time()
    cm.anotar_grafana(f"docker stop {contenedor} (inicio de la falla controlada)", ["falla", args.producto])
    codigo, salida = await asyncio.to_thread(docker, "stop", contenedor)
    eventos["stop_fin"] = time.time()
    eventos["stop_resultado"] = "ok" if codigo == 0 else f"error: {salida[:120]}"
    print(f"[{eventos['stop_fin'] - eventos['t0']:6.1f}s] docker stop {contenedor}: {eventos['stop_resultado']}")

    await asyncio.sleep(min(30, args.falla / 2))
    salud_registro["durante_la_falla"] = await asyncio.to_thread(salud, True)
    estado = salud_registro["durante_la_falla"].get("dependencias", {}).get(base, {})
    print(f"[{time.time() - eventos['t0']:6.1f}s] /health/dependencias -> {base}: {estado.get('estado')} ({estado.get('clasificacion')})")
    await asyncio.sleep(max(0.0, args.falla - (time.time() - eventos["stop_inicio"])))

    eventos["start_inicio"] = time.time()
    cm.anotar_grafana(f"docker start {contenedor} (recuperación)", ["recuperacion", args.producto])
    codigo, salida = await asyncio.to_thread(docker, "start", contenedor)
    eventos["start_fin"] = time.time()
    eventos["start_resultado"] = "ok" if codigo == 0 else f"error: {salida[:120]}"
    print(f"[{eventos['start_fin'] - eventos['t0']:6.1f}s] docker start {contenedor}: {eventos['start_resultado']}")

    # Recuperación vista por la API: se fuerza el diagnóstico cada 5 s (límite del Hito 11).
    limite = eventos["start_fin"] + args.recuperacion - 5
    while time.time() < limite:
        await asyncio.sleep(5)
        s = await asyncio.to_thread(salud, True)
        if s.get("dependencias", {}).get(base, {}).get("estado") == "up":
            eventos["api_ve_recuperada"] = time.time()
            salud_registro["despues_de_recuperar"] = s
            print(f"[{eventos['api_ve_recuperada'] - eventos['t0']:6.1f}s] la API vuelve a usar {base}")
            break


# ------------------------------------------------------------------ análisis
def primera_vez(series: list[dict], filtro: dict, condicion, desde: float) -> float | None:
    for s in series:
        if all(s["metric"].get(k) == v for k, v in filtro.items()):
            for ts, val in s["values"]:
                if float(ts) >= desde and condicion(float(val)):
                    return float(ts)
    return None


def tramos(eventos: dict) -> dict[str, tuple[float, float]]:
    t0, fin = eventos["t0"], eventos["fin_carga"]
    if "stop_inicio" not in eventos or "start_inicio" not in eventos:
        return {"carga": (t0, fin)}
    return {"antes": (t0, eventos["stop_inicio"]),
            "falla": (eventos["stop_fin"], eventos["start_inicio"]),
            "despues": (eventos.get("api_ve_recuperada", eventos["start_fin"]), fin)}


def resumen_cliente(filas, desde: float, hasta: float) -> dict:
    sel = [f for f in filas if desde <= f[0] < hasta]
    dur = max(hasta - desde, 1e-9)
    por_tipo = {}
    for tipo in TIPO_A_BASE:
        st = [f for f in sel if f[1] == tipo]
        ok = [f[3] for f in st if 200 <= f[2] < 300]
        por_tipo[TIPO_A_BASE[tipo]] = {
            "solicitudes": len(st), "ok_2xx": len(ok), "errores_5xx": sum(1 for f in st if f[2] >= 500),
            "no_encontrado_404": sum(1 for f in st if f[2] == 404),
            "sin_respuesta": sum(1 for f in st if f[2] <= 0),
            "p50_ms": percentil(ok, .5), "p95_ms": percentil(ok, .95)}
    ok_all = [f[3] for f in sel if 200 <= f[2] < 300]
    return {"duracion_s": round(dur, 1), "solicitudes": len(sel), "rps": round(len(sel) / dur, 1),
            "errores_5xx": sum(1 for f in sel if f[2] >= 500),
            "tasa_5xx_pct": round(100 * sum(1 for f in sel if f[2] >= 500) / len(sel), 2) if sel else None,
            "p50_ms": percentil(ok_all, .5), "p95_ms": percentil(ok_all, .95), "por_base": por_tipo}


def graficar(series: dict, eventos: dict, base: str | None, ruta: Path, titulo: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t0 = eventos["t0"]
    fig, ejes = plt.subplots(4, 1, figsize=(12, 13), sharex=True)
    def dibujar(ax, clave, etiqueta, escala=1.0, filtro=None):
        for s in series.get(clave, []):
            nombre = s["metric"].get(etiqueta, "P95 global")
            if filtro and nombre not in filtro:
                continue
            xs = [float(ts) - t0 for ts, _ in s["values"]]
            ys = [float(v) * escala if v not in ("NaN", "+Inf") else float("nan") for _, v in s["values"]]
            ax.plot(xs, ys, label=nombre, linewidth=1.8)
    dibujar(ejes[0], "dependencia_up", "dependencia")
    for s in series.get("sonda_tcp", []):
        if base and s["metric"].get("componente") == base:
            ejes[0].plot([float(ts) - t0 for ts, _ in s["values"]], [float(v) - 0.05 for _, v in s["values"]],
                         "k--", linewidth=1.2, label=f"sonda TCP {base} (−0,05 para distinguirla)")
    ejes[0].set_ylabel("1 = disponible")
    ejes[0].set_title("Disponibilidad: fixture_dependencia_up (API → base) y probe_success (puerto)")
    dibujar(ejes[1], "rps_por_base", "dependencia")
    ejes[1].set_ylabel("solicitudes/s")
    ejes[1].set_title("Throughput por base: rate(fixture_http_requests_total[1m])")
    dibujar(ejes[2], "errores_5xx_por_base", "dependencia")
    ejes[2].set_ylabel("5xx/s")
    ejes[2].set_title("Errores 5xx por base: rate(fixture_http_requests_total{codigo=~\"5..\"}[1m])")
    dibujar(ejes[3], "p95_global", "x", escala=1000)
    dibujar(ejes[3], "p95_por_base", "dependencia", escala=1000)
    ejes[3].axhline(250, color="red", linestyle=":", linewidth=1.2, label="umbral alerta 250 ms")
    ejes[3].set_ylabel("ms")
    ejes[3].set_title("Latencia P95 de la API (histograma, ventana 1 min)")
    ejes[3].set_xlabel("segundos desde el inicio de la prueba")
    for ax in ejes:
        if "stop_inicio" in eventos:
            ax.axvspan(eventos["stop_inicio"] - t0, eventos["start_fin"] - t0, color="red", alpha=0.08)
            ax.axvline(eventos["stop_inicio"] - t0, color="red", linewidth=1)
            ax.axvline(eventos["start_fin"] - t0, color="green", linewidth=1)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="upper right", ncol=3)
    fig.suptitle(titulo, fontsize=11)
    fig.tight_layout()
    fig.savefig(ruta, dpi=110)
    plt.close(fig)


# ------------------------------------------------------------------ principal
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--producto", default="redis", choices=[*cm.CONTENEDORES, "ninguno"])
    ap.add_argument("--usuarios", type=int, default=20)
    ap.add_argument("--normal", type=int, default=60, help="segundos de tráfico antes de la falla")
    ap.add_argument("--falla", type=int, default=120, help="segundos con la base detenida")
    ap.add_argument("--recuperacion", type=int, default=90, help="segundos de tráfico después del start")
    ap.add_argument("--espera-final", type=int, default=45)
    ap.add_argument("--semilla", type=int, default=2030)
    args = ap.parse_args()

    contenedor, base = cm.CONTENEDORES.get(args.producto, (None, None))
    con_falla = contenedor is not None

    print(f"=== HITO 13 - PRUEBA CONTROLADA ({'falla de ' + base if con_falla else 'solo carga'}) ===")
    try:
        httpx.get(f"{cm.API}/health/live", timeout=5).raise_for_status()
    except Exception as error:  # noqa: BLE001
        print(f"[ERROR] La API no responde en {cm.API}: {type(error).__name__}")
        return 1
    if not cm.prom_disponible():
        print("[ERROR] Prometheus no responde: ejecutar antes scripts\\iniciar_monitoreo.ps1")
        return 1
    if con_falla and not contenedor_corriendo(contenedor):
        print(f"[ERROR] {contenedor} no está corriendo: la prueba debe empezar con la base disponible.")
        return 1
    if not CATALOGO.exists():
        print("[ERROR] Falta el catálogo de claves del Hito 12 (datos-o-generadores/catalogo_claves.json).")
        return 1

    print("Refrescando sesiones sintéticas de Redis del Hito 12...", refrescar_sesiones_redis())
    try:
        info_api = httpx.get(f"{cm.API}/metrics", timeout=10).text
        linea_info = next(l for l in info_api.splitlines() if l.startswith("fixture_api_info{"))
        config_api = dict(par.split("=", 1) for par in linea_info[linea_info.index("{") + 1:linea_info.index("}")].replace('"', "").split(","))
    except Exception:  # noqa: BLE001
        config_api = {}
    corte = config_api.get("corte_rapido_segundos", "0")
    print(f"Configuración de la API: IRIS_POOL_SIZE={config_api.get('iris_pool_size')} | CORTE_RAPIDO_SEGUNDOS={corte}")

    duracion = args.normal + (args.falla + args.recuperacion if con_falla else 0)
    salud_registro = {"antes": salud(True)}
    print(f"Estado previo: {salud_registro['antes'].get('estado_general')} | usuarios: {args.usuarios} | duración: {duracion} s")

    gen = Generador(args.usuarios, args.semilla)
    eventos: dict = {"t0": time.time()}
    cm.anotar_grafana(f"Inicio prueba controlada ({args.usuarios} usuarios, {args.producto})", ["inicio", args.producto])

    async def todo():
        await asyncio.gather(gen.correr(duracion), orquestar(args, contenedor, base, eventos, salud_registro))

    try:
        asyncio.run(todo())
    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
    finally:
        if con_falla and not contenedor_corriendo(contenedor):
            print(f"Reiniciando {contenedor} (la prueba nunca deja una base detenida)...")
            docker("start", contenedor)
    eventos["fin_carga"] = time.time()
    cm.anotar_grafana("Fin de la carga", ["fin", args.producto])
    salud_registro["al_final"] = salud(True)

    print(f"Carga terminada: {len(gen.filas)} solicitudes. Esperando {args.espera_final} s para que Prometheus registre el final...")
    time.sleep(args.espera_final)

    # ----------------------------------------------------------- Prometheus
    desde, hasta = eventos["t0"] - 60, time.time()
    neg = 'ruta=~"/api/v1/.*"'
    consultas = {
        "dependencia_up": "max by (dependencia) (fixture_dependencia_up)",
        "sonda_tcp": 'max by (componente) (probe_success{job="sonda-tcp"})',
        "exporter_up": 'max by (job) ({__name__=~"redis_up|mongodb_up"})',
        "rps_por_base": f"sum by (dependencia) (rate(fixture_http_requests_total{{{neg}}}[1m]))",
        "errores_5xx_por_base": f'sum by (dependencia) (rate(fixture_http_requests_total{{{neg}, codigo=~"5.."}}[1m]))',
        "p95_global": f"histogram_quantile(0.95, sum by (le) (rate(fixture_http_request_duration_seconds_bucket{{{neg}}}[1m])))",
        "p95_por_base": f"histogram_quantile(0.95, sum by (le, dependencia) (rate(fixture_http_request_duration_seconds_bucket{{{neg}}}[1m])))",
        "cpu_api_pct": "rate(fixture_api_proceso_cpu_segundos_total[1m]) * 100",
        "corte_rapido_rechazos": "sum by (dependencia) (rate(fixture_corte_rapido_rechazos_total[1m]))",
        "alertas": 'ALERTS{alertname=~"Fixture.*|Redis.*|Iris.*"}',
    }
    series = {}
    for clave, expr in consultas.items():
        try:
            series[clave] = cm.prom_rango(expr, desde, hasta, "5s")
        except Exception as error:  # noqa: BLE001
            series[clave] = []
            print(f"[AVISO] No se pudo consultar {clave}: {type(error).__name__}")

    linea = {"t0": datetime.fromtimestamp(eventos["t0"], cm.TZ).isoformat(timespec="seconds")}
    rel = lambda ts: None if ts is None else round(ts - eventos["t0"], 1)  # noqa: E731
    for k in ("stop_inicio", "stop_fin", "start_inicio", "start_fin", "api_ve_recuperada", "fin_carga"):
        if k in eventos:
            linea[f"{k}_s"] = rel(eventos[k])
    alertas_vistas: dict[str, dict] = {}
    if con_falla and "start_inicio" in eventos:
        caida_prom = primera_vez(series["dependencia_up"], {"dependencia": base}, lambda v: v == 0, eventos["stop_inicio"])
        caida_sonda = primera_vez(series["sonda_tcp"], {"componente": base}, lambda v: v == 0, eventos["stop_inicio"])
        vuelta_prom = primera_vez(series["dependencia_up"], {"dependencia": base}, lambda v: v == 1, eventos["start_inicio"])
        vuelta_sonda = primera_vez(series["sonda_tcp"], {"componente": base}, lambda v: v == 1, eventos["start_inicio"])
        linea.update({
            "prometheus_registra_caida_api_s": rel(caida_prom),
            "prometheus_registra_puerto_cerrado_s": rel(caida_sonda),
            "deteccion_desde_stop_api_s": None if caida_prom is None else round(caida_prom - eventos["stop_inicio"], 1),
            "deteccion_desde_stop_sonda_s": None if caida_sonda is None else round(caida_sonda - eventos["stop_inicio"], 1),
            "prometheus_registra_recuperacion_api_s": rel(vuelta_prom),
            "recuperacion_desde_start_api_s": None if vuelta_prom is None else round(vuelta_prom - eventos["start_inicio"], 1),
            "recuperacion_desde_start_sonda_s": None if vuelta_sonda is None else round(vuelta_sonda - eventos["start_inicio"], 1),
            "recuperacion_vista_por_la_api_s": None if "api_ve_recuperada" not in eventos else round(eventos["api_ve_recuperada"] - eventos["start_inicio"], 1),
        })
    for s in series["alertas"]:
        m = s["metric"]
        clave = f"{m.get('alertname')} [{m.get('alertstate')}] {m.get('dependencia') or m.get('componente') or m.get('job') or ''}".strip()
        tss = [float(ts) for ts, _ in s["values"]]
        alertas_vistas[clave] = {"desde_s": rel(min(tss)), "hasta_s": rel(max(tss)),
                                 "ya_estaba_antes_de_la_prueba": min(tss) <= eventos["t0"]}
    linea["alertas"] = alertas_vistas

    resumen = {
        "fecha": cm.ahora_iso(), "commit": cm.commit_actual(), "producto": args.producto, "contenedor": contenedor,
        "parametros": {k: v for k, v in vars(args).items()},
        "config_api": config_api,
        "mezcla_y_claves": "Hito 12: configuracion-ejemplo.json + catalogo_claves.json (solo lecturas GET)",
        "cliente_por_tramo": {n: resumen_cliente(gen.filas, a, b) for n, (a, b) in tramos(eventos).items()},
        "cliente_total": resumen_cliente(gen.filas, eventos["t0"], eventos["fin_carga"]),
        "linea_de_tiempo": linea,
    }
    if "falla" in resumen["cliente_por_tramo"]:
        falla = resumen["cliente_por_tramo"]["falla"]["por_base"]
        resumen["aislamiento"] = {
            "errores_5xx_en_la_base_detenida": falla[base]["errores_5xx"],
            "errores_5xx_en_las_otras_bases": sum(v["errores_5xx"] for k, v in falla.items() if k != base),
            "conclusion": ("las demás bases siguieron respondiendo sin errores"
                           if sum(v["errores_5xx"] for k, v in falla.items() if k != base) == 0
                           else "hubo errores en otras bases: revisar"),
        }

    etiqueta_corte = f"corte{int(float(corte))}" if con_falla else f"{args.usuarios}vus"
    carpeta = cm.EVIDENCIA_DIR / f"prueba_de_falla_{args.producto}_{etiqueta_corte}_{cm.sello()}"
    carpeta.mkdir(parents=True, exist_ok=True)
    cm.escribir_json(carpeta / "resumen.json", resumen)
    cm.escribir_json(carpeta / "linea_de_tiempo.json", linea)
    cm.escribir_json(carpeta / "salud_dependencias.json", salud_registro)
    cm.escribir_json(carpeta / "prometheus_series.json", {"consultas": consultas, "desde": desde, "hasta": hasta,
                                                          "paso": "5s", "series": series})
    conteo = Counter((int(f[0] - eventos["t0"]), f[1], f[2]) for f in gen.filas)
    with (carpeta / "solicitudes_por_segundo.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["segundo", "base", "codigo_http", "solicitudes"])
        for (seg, tipo, codigo), n in sorted(conteo.items()):
            w.writerow([seg, TIPO_A_BASE[tipo], codigo, n])
    titulo = (f"Hito 13 - prueba controlada: {'docker stop/start de ' + contenedor if con_falla else 'solo carga'}"
              f" con {args.usuarios} usuarios ({resumen['fecha']})")
    try:
        graficar(series, eventos, base, carpeta / "prueba_controlada.png", titulo)
    except Exception as error:  # noqa: BLE001
        print(f"[AVISO] No se pudo generar el gráfico: {type(error).__name__}: {error}")

    escribir_markdown(resumen, carpeta)
    print(f"\nEvidencia: {carpeta.relative_to(cm.HITO_DIR)}")
    print(json.dumps(linea, ensure_ascii=False, indent=2))
    if "aislamiento" in resumen:
        print(json.dumps(resumen["aislamiento"], ensure_ascii=False, indent=2))
    return 0


def escribir_markdown(r: dict, carpeta: Path) -> None:
    lt = r["linea_de_tiempo"]
    rel = carpeta.relative_to(cm.EVIDENCIA_DIR).as_posix()
    md = [f"# Prueba controlada - {r['producto']} ({r['fecha']})", "",
          f"Generado por `scripts/ejecutar_prueba_controlada.py` · commit `{r['commit']}` · carpeta [`{rel}/`]({rel}/)", "",
          f"Configuración de la API: `IRIS_POOL_SIZE={r['config_api'].get('iris_pool_size')}`, "
          f"`CORTE_RAPIDO_SEGUNDOS={r['config_api'].get('corte_rapido_segundos', '0 (no existía)')}`.", "",
          f"Parámetros: {r['parametros']['usuarios']} usuarios virtuales constantes, {r['parametros']['normal']} s normales"
          + (f", {r['parametros']['falla']} s con `{r['contenedor']}` detenido, {r['parametros']['recuperacion']} s de recuperación."
             if r["contenedor"] else "."), "",
          "## Lado cliente (medido por el generador)", "",
          "| Tramo | Duración (s) | Solicitudes | req/s | 5xx | % 5xx | P50 ms | P95 ms |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for n, t in r["cliente_por_tramo"].items():
        md.append(f"| {n} | {t['duracion_s']} | {t['solicitudes']} | {t['rps']} | {t['errores_5xx']} | {t['tasa_5xx_pct']} | {t['p50_ms']} | {t['p95_ms']} |")
    if "falla" in r["cliente_por_tramo"]:
        md += ["", "Durante la falla, por base:", "", "| Base | Solicitudes | 2xx | 5xx | P95 ms (2xx) |", "|---|---:|---:|---:|---:|"]
        for b, v in r["cliente_por_tramo"]["falla"]["por_base"].items():
            md.append(f"| {b} | {v['solicitudes']} | {v['ok_2xx']} | {v['errores_5xx']} | {v['p95_ms']} |")
        md += ["", f"**Aislamiento:** {r['aislamiento']['conclusion']} "
               f"({r['aislamiento']['errores_5xx_en_la_base_detenida']} errores 5xx en la base detenida, "
               f"{r['aislamiento']['errores_5xx_en_las_otras_bases']} en las demás)."]
    md += ["", "## Línea de tiempo (segundos desde el inicio)", "", "| Evento | s |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in lt.items() if k not in ("alertas", "t0")]
    md += ["", "## Alertas registradas por Prometheus (serie ALERTS)", "",
           "Una alerta pasa a *pending* cuando se cumple la condición y a *firing* cuando se mantiene durante su `for`.", "",
           "| Alerta [estado] objeto | desde s | hasta s | ¿ya estaba antes? |", "|---|---:|---:|---|"]
    md += [f"| {k} | {v['desde_s']} | {v['hasta_s']} | {'sí' if v['ya_estaba_antes_de_la_prueba'] else 'no'} |"
           for k, v in lt.get("alertas", {}).items()] or ["| (ninguna) | | | |"]
    md += ["", f"![Prueba controlada]({rel}/prueba_controlada.png)", ""]
    texto = "\n".join(md) + "\n"
    local = texto.replace(f" · carpeta [`{rel}/`]({rel}/)", "").replace(f"]({rel}/prueba_controlada.png)", "](prueba_controlada.png)")
    (carpeta / "README.md").write_text(local, encoding="utf-8")
    (cm.EVIDENCIA_DIR / "prueba_de_falla.md" if r["contenedor"] else cm.EVIDENCIA_DIR / "prueba_de_carga.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
