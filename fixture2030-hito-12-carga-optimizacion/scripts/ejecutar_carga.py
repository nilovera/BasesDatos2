"""GENERACIÓN DE CARGA + MEDICIÓN del Hito 12.

Generador de modelo cerrado: N usuarios virtuales (VUs) que repiten "elegir operación -> GET a
la API -> esperar think time". El número de VUs sigue las fases del escenario (calentamiento,
rampa, sostenimiento, pico, recuperación) definidas en config/.

Versión 2: los VUs se reparten entre varios PROCESOS (config "procesos_generador"). En la primera
línea base (v1) un único proceso Python llegó al 100% de un núcleo y era el generador, no la API,
el que limitaba el throughput. Con varios procesos el generador deja de ser el cuello de botella.
Todos los procesos siguen el mismo reloj (hora de inicio común), así que las fases son simultáneas.

Mide, por solicitud: latencia vista por el cliente, tiempo informado por la API (X-Process-Time-Ms),
código HTTP, tipo de error e integridad del contenido (huella vs. catálogo).
En paralelo muestrea recursos: CPU/RAM del sistema, del proceso de la API, de los procesos del
generador y de cada contenedor (docker stats), y el retraso del event loop de cada proceso.

Uso:
    python ejecutar_carga.py --escenario humo     --etiqueta humo
    python ejecutar_carga.py --escenario completo --etiqueta linea_base
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import gzip
import json
import math
import multiprocessing as mp
import pickle
import random
import subprocess
import sys
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import httpx

import comun

try:
    import psutil
except ImportError:  # el script funciona igual, pero sin métricas de CPU/RAM
    psutil = None


# ------------------------------------------------------------------ estadística
def percentil(ordenados: list[float], p: float) -> float:
    """Percentil con interpolación lineal (mismo criterio que numpy 'linear')."""
    if not ordenados:
        return float("nan")
    k = (len(ordenados) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return ordenados[int(k)]
    return ordenados[f] + (ordenados[c] - ordenados[f]) * (k - f)


def resumir(filas: list[dict], duracion_s: float) -> dict:
    lat = sorted(f["latencia_ms"] for f in filas if f["error"] == "")
    api = sorted(f["api_ms"] for f in filas if f["error"] == "" and f["api_ms"] is not None)
    errores = defaultdict(int)
    for f in filas:
        if f["error"]:
            errores[f["error"]] += 1
    ok = len(lat)
    total = len(filas)
    r2 = lambda v: None if v is None or (isinstance(v, float) and math.isnan(v)) else round(v, 2)  # noqa: E731
    return {
        "solicitudes": total,
        "exitosas": ok,
        "fallidas": total - ok,
        "tasa_error_pct": r2(100 * (total - ok) / total) if total else None,
        "errores_por_tipo": dict(errores),
        "throughput_ok_rps": r2(ok / duracion_s) if duracion_s else None,
        "latencia_ms": {
            "min": r2(lat[0]) if lat else None,
            "promedio": r2(sum(lat) / ok) if ok else None,
            "p50": r2(percentil(lat, .50)), "p90": r2(percentil(lat, .90)),
            "p95": r2(percentil(lat, .95)), "p99": r2(percentil(lat, .99)),
            "max": r2(lat[-1]) if lat else None,
        },
        "api_ms": {"p50": r2(percentil(api, .50)), "p95": r2(percentil(api, .95)), "p99": r2(percentil(api, .99))},
        "integridad": {
            "ok": sum(1 for f in filas if f["integridad"] == "ok"),
            "alterada": sum(1 for f in filas if f["integridad"] == "alterada"),
            "no_verificable": sum(1 for f in filas if f["integridad"] == "no_verificable"),
        },
    }


# ------------------------------------------------------------------ plan de fases (reloj común)
def plan(fases: list[dict], t: float) -> tuple[dict | None, int]:
    """Fase y VUs objetivo en el segundo t desde el inicio. (None, 0) cuando terminó."""
    acumulado = 0.0
    for fase in fases:
        if t < acumulado + fase["duracion_s"]:
            frac = (t - acumulado) / fase["duracion_s"]
            return fase, round(fase["vus_inicio"] + (fase["vus_fin"] - fase["vus_inicio"]) * frac)
        acumulado += fase["duracion_s"]
    return None, 0


# ------------------------------------------------------------------ proceso generador
async def _correr_proceso(idx: int, nproc: int, cfg: dict, fases: list[dict], claves: dict,
                          t_inicio: float, abortar) -> dict:
    max_vus = max(max(f["vus_inicio"], f["vus_fin"]) for f in fases)
    mis_vus = [v for v in range(max_vus) if v % nproc == idx]
    estado = {"fin": False, "objetivo": 0, "fase": "espera", "medir": False, "corte": ""}
    filas: list[dict] = []
    lag_por_seg: dict[int, float] = {}
    # reloj: t_s = segundos desde t_inicio (hora de pared común a todos los procesos)
    p0 = time.perf_counter() - (time.time() - t_inicio)
    reloj = lambda: time.perf_counter() - p0  # noqa: E731

    tipos = list(cfg["mezcla_operaciones"].keys())
    pesos = list(cfg["mezcla_operaciones"].values())
    pmin, pmax = cfg["think_time_ms"]
    corte = cfg["corte_seguro"]

    async def usuario_virtual(vu: int, cliente: httpx.AsyncClient) -> None:
        rng = random.Random(cfg["semilla"] * 10_000 + vu)
        while not estado["fin"]:
            if vu >= estado["objetivo"]:
                await asyncio.sleep(0.1)
                continue
            tipo = rng.choices(tipos, pesos)[0]
            calientes = claves.get(f"{tipo}__caliente") or []
            entrada = (rng.choice(calientes) if calientes and rng.random() < cfg["probabilidad_clave_caliente"]
                       else rng.choice(claves[tipo]))
            rid = str(uuid.uuid4())
            fase, medir, vus = estado["fase"], estado["medir"], estado["objetivo"]
            t_s = reloj()
            inicio = time.perf_counter()
            status, api_ms, error, integridad = 0, None, "", "n/a"
            try:
                resp = await cliente.get(entrada["url"], headers={"X-Request-ID": rid})
                latencia = (time.perf_counter() - inicio) * 1000
                status = resp.status_code
                try:
                    api_ms = float(resp.headers.get("X-Process-Time-Ms"))
                except (TypeError, ValueError):
                    api_ms = None
                if status == 200:
                    h = comun.huella(resp.json())
                    if h == entrada["huella"]:
                        integridad = "ok"
                    elif entrada["determinista"]:
                        integridad, error = "alterada", "integridad"
                    else:
                        integridad = "no_verificable"
                else:
                    error = f"http_{status}"
            except httpx.TimeoutException:
                latencia, error = (time.perf_counter() - inicio) * 1000, "timeout"
            except httpx.TransportError as exc:
                latencia, error = (time.perf_counter() - inicio) * 1000, f"conexion_{type(exc).__name__}"
            filas.append({
                "request_id": rid, "t_s": round(t_s, 3), "fase": fase, "medida": medir, "vus": vus, "vu": vu,
                "proceso": idx, "tipo": tipo, "clave": entrada["clave"], "status": status,
                "latencia_ms": round(latencia, 2), "api_ms": api_ms, "error": error, "integridad": integridad,
            })
            await asyncio.sleep(rng.uniform(pmin, pmax) / 1000)

    async def controlar() -> None:
        while not estado["fin"]:
            t = reloj()
            if t < 0:
                await asyncio.sleep(min(0.1, -t))
                continue
            fase, objetivo = plan(fases, t)
            if fase is None or abortar.is_set():
                estado["fin"] = True
                break
            estado.update(fase=fase["nombre"], medir=fase.get("medir", True), objetivo=objetivo)
            recientes = [f for f in filas[-1500:] if f["t_s"] >= t - corte["ventana_s"]]
            if len(recientes) >= 30 and sum(1 for f in recientes if f["error"]) / len(recientes) > corte["tasa_error_maxima"]:
                estado["corte"] = (f"corte seguro: >{corte['tasa_error_maxima']:.0%} de error en "
                                   f"{corte['ventana_s']} s (fase {fase['nombre']}, proceso {idx}, t={t:.0f}s)")
                abortar.set()
                estado["fin"] = True
                break
            await asyncio.sleep(0.1)
        estado["objetivo"] = 0

    async def medir_lag() -> None:
        """Retraso del event loop: si crece, ESTE proceso generador no da abasto."""
        while not estado["fin"]:
            t = time.perf_counter()
            await asyncio.sleep(0.1)
            lag = (time.perf_counter() - t - 0.1) * 1000
            seg = int(reloj())
            lag_por_seg[seg] = max(lag_por_seg.get(seg, 0.0), lag)

    limites = httpx.Limits(max_connections=len(mis_vus) + 5, max_keepalive_connections=len(mis_vus) + 5)
    async with httpx.AsyncClient(base_url=cfg["api_base_url"], timeout=cfg["timeout_segundos"], limits=limites) as cliente:
        tareas = [asyncio.create_task(usuario_virtual(v, cliente)) for v in mis_vus]
        tareas += [asyncio.create_task(medir_lag())]
        await controlar()
        await asyncio.gather(*tareas, return_exceptions=True)
    return {"filas": filas, "lag": lag_por_seg, "corte": estado["corte"]}


def proceso_generador(idx, nproc, cfg, fases, claves, t_inicio, abortar, ruta_parte) -> None:
    resultado = asyncio.run(_correr_proceso(idx, nproc, cfg, fases, claves, t_inicio, abortar))
    with open(ruta_parte, "wb") as fh:
        pickle.dump(resultado, fh)


# ------------------------------------------------------------------ monitor de recursos (proceso principal)
class MonitorRecursos(threading.Thread):
    def __init__(self, intervalo: float, t_inicio: float, fases: list[dict], generadores: list) -> None:
        super().__init__(daemon=True)
        self.intervalo, self.t_inicio, self.fases = intervalo, t_inicio, fases
        self.muestras: list[dict] = []
        self.parar = threading.Event()
        self.api_procs = self._procesos_api()
        self.gen_procs = []
        if psutil:
            self.gen_procs = [psutil.Process()] + [psutil.Process(p.pid) for p in generadores]
            psutil.cpu_percent(None)
            for p in self.api_procs + self.gen_procs:
                try:
                    p.cpu_percent(None)
                except Exception:  # noqa: BLE001
                    pass

    @staticmethod
    def _procesos_api() -> list:
        if not psutil:
            return []
        try:
            raiz = psutil.Process(int((comun.API_ROOT / ".api.pid").read_text().strip()))
            return [raiz] + raiz.children(recursive=True)
        except Exception:  # noqa: BLE001
            for c in psutil.net_connections(kind="tcp"):
                if c.laddr and c.laddr.port == 8000 and c.status == "LISTEN" and c.pid:
                    return [psutil.Process(c.pid)]
        return []

    @staticmethod
    def _sumar(procs: list) -> tuple[float, float, int]:
        cpu = rss = hilos = 0
        for p in procs:
            try:
                cpu += p.cpu_percent(None)
                rss += p.memory_info().rss
                hilos += p.num_threads()
            except Exception:  # noqa: BLE001
                pass
        return round(cpu, 1), round(rss / 1024 ** 2, 1), hilos

    def _docker(self) -> dict:
        try:
            salida = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{json .}}"],
                                    capture_output=True, text=True, timeout=15).stdout
        except Exception:  # noqa: BLE001
            return {}
        datos = {}
        for linea in salida.splitlines():
            try:
                d = json.loads(linea)
            except json.JSONDecodeError:
                continue
            if "fixture2030" in d.get("Name", ""):
                nombre = d["Name"].replace("fixture2030-", "")
                datos[f"{nombre}_cpu_pct"] = float(d["CPUPerc"].rstrip("%") or 0)
                datos[f"{nombre}_mem"] = d["MemUsage"].split("/")[0].strip()
        return datos

    def run(self) -> None:
        while not self.parar.is_set():
            inicio = time.perf_counter()
            t = time.time() - self.t_inicio
            fase, vus = plan(self.fases, t)
            nombre = "espera" if t < 0 else (fase["nombre"] if fase else "fin")
            m = {"t_s": round(t, 1), "fase": nombre, "vus": vus if t >= 0 else 0}
            if psutil:
                m["sistema_cpu_pct"] = psutil.cpu_percent(None)
                m["sistema_ram_pct"] = psutil.virtual_memory().percent
                m["api_cpu_pct"], m["api_ram_mb"], m["api_hilos"] = self._sumar(self.api_procs)
                m["generador_cpu_pct"], m["generador_ram_mb"], _ = self._sumar(self.gen_procs)
            m.update(self._docker())
            self.muestras.append(m)
            self.parar.wait(max(0.0, self.intervalo - (time.perf_counter() - inicio)))


# ------------------------------------------------------------------ utilidades
def preparar_claves(cfg: dict) -> dict[str, list[dict]]:
    if not comun.CATALOGO_PATH.exists():
        raise SystemExit("[ERROR] Falta el catálogo de claves. Ejecutar antes scripts\\preparar_datos.py")
    catalogo = json.loads(comun.CATALOGO_PATH.read_text(encoding="utf-8"))["claves"]
    claves: dict[str, list[dict]] = defaultdict(list)
    for e in catalogo:
        claves[e["tipo"]].append(e)
        if e.get("partido") == cfg["partido_caliente"] or e["clave"] == cfg["equipo_caliente"]:
            claves[f"{e['tipo']}__caliente"].append(e)
    faltan = [t for t in cfg["mezcla_operaciones"] if not claves.get(t)]
    if faltan:
        raise SystemExit(f"[ERROR] El catálogo no tiene claves para: {faltan}")
    return dict(claves)


def serie_temporal(filas: list[dict], paso: int = 5) -> list[dict]:
    cubos: dict[int, list[dict]] = defaultdict(list)
    for f in filas:
        cubos[int(f["t_s"] // paso)].append(f)
    serie = []
    for k in sorted(cubos):
        grupo = cubos[k]
        lat = sorted(f["latencia_ms"] for f in grupo if not f["error"])
        api = sorted(f["api_ms"] for f in grupo if not f["error"] and f["api_ms"] is not None)
        iris = sorted(f["latencia_ms"] for f in grupo if not f["error"] and f["tipo"] == "detalle_iris")
        serie.append({
            "t_s": k * paso, "fase": grupo[-1]["fase"], "vus": max(f["vus"] for f in grupo),
            "rps_ok": round(len(lat) / paso, 1), "errores": sum(1 for f in grupo if f["error"]),
            "p50_ms": round(percentil(lat, .5), 1) if lat else None,
            "p95_ms": round(percentil(lat, .95), 1) if lat else None,
            "api_p95_ms": round(percentil(api, .95), 1) if api else None,
            "iris_p95_ms": round(percentil(iris, .95), 1) if iris else None,
        })
    return serie


def escribir_csv(ruta: Path, filas: list[dict], comprimir: bool = False) -> None:
    if not filas:
        return
    campos: list[str] = []
    for f in filas:
        for k in f:
            if k not in campos:
                campos.append(k)
    abrir = (lambda: gzip.open(ruta, "wt", encoding="utf-8", newline="")) if comprimir else \
        (lambda: ruta.open("w", encoding="utf-8", newline=""))
    with abrir() as fh:
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


# ------------------------------------------------------------------ principal
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escenario", default="completo")
    ap.add_argument("--etiqueta", required=True, help="humo | linea_base | optimizada | ...")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = comun.cargar_config(args.config)
    fases = cfg["escenarios"][args.escenario]
    nproc = int(cfg.get("procesos_generador", 1))
    claves = preparar_claves(cfg)
    try:
        httpx.get(f"{cfg['api_base_url']}/health", timeout=5).raise_for_status()
    except Exception as error:  # noqa: BLE001
        print(f"[ERROR] La API no responde: {type(error).__name__}")
        return 1
    # /health/ready (agregado en el Hito 11) confirma que las 6 dependencias responden antes de medir.
    try:
        listo = httpx.get(f"{cfg['api_base_url']}/health/ready", timeout=15)
        estado_ready = {"http": listo.status_code, "cuerpo": listo.json()}
    except Exception as error:  # noqa: BLE001
        estado_ready = {"http": None, "error": type(error).__name__}
    if estado_ready.get("http") != 200:
        print(f"[AVISO] /health/ready no devolvió 200: {estado_ready}. Revisar que estén los 6 contenedores.")

    sello = datetime.now(comun.TZ).strftime("%Y%m%d-%H%M%S")
    salida = comun.EVIDENCIA_DIR / f"{args.etiqueta}_{sello}"
    salida.mkdir(parents=True, exist_ok=True)
    metadatos = {
        "etiqueta": args.etiqueta, "escenario": args.escenario, "inicio": comun.ahora_iso(),
        "git": comun.info_git(), "config_api": comun.info_config_api(), "versiones": comun.info_versiones(),
        "hardware": comun.info_hardware(), "contenedores": comun.info_contenedores(),
        "health_ready_previo": estado_ready,
        "config_prueba": {k: v for k, v in cfg.items() if k != "escenarios"} | {"fases": fases},
        "catalogo": json.loads(comun.CATALOGO_PATH.read_text(encoding="utf-8"))["resumen"],
        "herramienta": f"generador propio asyncio + httpx, modelo cerrado, {nproc} procesos",
    }
    duracion = sum(f["duracion_s"] for f in fases)
    print(f"=== HITO 12 - CARGA '{args.etiqueta}' (escenario {args.escenario}) ===")
    print(f"Commit API: {metadatos['git']['commit']} | IRIS_POOL_SIZE: {metadatos['config_api'].get('iris_pool_size')}")
    print(f"Duración prevista: {duracion} s | VUs máx: {max(f['vus_fin'] for f in fases)} | procesos generador: {nproc}")

    ctx = mp.get_context("spawn")
    abortar = ctx.Event()
    t_inicio = time.time() + 5          # margen para que arranquen todos los procesos
    partes = [salida / f"_parte_{i}.pkl" for i in range(nproc)]
    procesos = [ctx.Process(target=proceso_generador, args=(i, nproc, cfg, fases, claves, t_inicio, abortar, partes[i]))
                for i in range(nproc)]
    for p in procesos:
        p.start()
    monitor = MonitorRecursos(cfg["intervalo_muestreo_recursos_s"], t_inicio, fases, procesos)
    monitor.start()

    fase_impresa = None
    try:
        while any(p.is_alive() for p in procesos):
            t = time.time() - t_inicio
            fase, vus = plan(fases, t)
            if t >= 0 and fase and fase["nombre"] != fase_impresa:
                fase_impresa = fase["nombre"]
                print(f"[{t:6.1f}s] fase {fase['nombre']:<14} VUs {fase['vus_inicio']}->{fase['vus_fin']} durante {fase['duracion_s']} s")
            time.sleep(0.5)
    except KeyboardInterrupt:
        abortar.set()
        print("Interrumpido: esperando que los procesos cierren...")
    for p in procesos:
        p.join(timeout=60)
    monitor.parar.set()
    monitor.join(timeout=20)

    filas: list[dict] = []
    lag: dict[int, float] = {}
    cortes = []
    for ruta in partes:
        if not ruta.exists():
            cortes.append(f"falta la parte {ruta.name} (proceso terminó con error)")
            continue
        with ruta.open("rb") as fh:
            parte = pickle.load(fh)
        ruta.unlink()
        filas.extend(parte["filas"])
        for s, v in parte["lag"].items():
            lag[s] = max(lag.get(s, 0.0), v)
        if parte["corte"]:
            cortes.append(parte["corte"])
    filas.sort(key=lambda f: f["t_s"])
    for m in monitor.muestras:      # retraso máximo del event loop entre todos los procesos en la ventana
        segs = [lag[s] for s in range(int(m["t_s"]) - 2, int(m["t_s"]) + 1) if s in lag]
        m["lag_loop_max_ms"] = round(max(segs), 1) if segs else None

    # duraciones reales por fase (si hubo corte, la última fase queda truncada)
    fin_real = max((f["t_s"] for f in filas), default=0) if cortes else duracion
    tiempos, acumulado = [], 0.0
    for fase in fases:
        if acumulado >= fin_real:
            break
        tiempos.append({**fase, "duracion_real_s": round(min(fase["duracion_s"], fin_real - acumulado), 1)})
        acumulado += fase["duracion_s"]
    metadatos.update(fin=comun.ahora_iso(), duraciones_reales=tiempos, corte="; ".join(cortes) or "no")

    medidas = [f for f in filas if f["medida"]]
    dur = {t["nombre"]: t["duracion_real_s"] for t in tiempos}
    dur_medida = sum(t["duracion_real_s"] for t in tiempos if t.get("medir", True))
    resumen = {
        "etiqueta": args.etiqueta, "escenario": args.escenario, "commit": metadatos["git"]["commit"],
        "iris_pool_size": metadatos["config_api"].get("iris_pool_size"), "procesos_generador": nproc,
        "corte": metadatos["corte"],
        "global_medido": resumir(medidas, dur_medida),
        "por_fase": {n: resumir([f for f in filas if f["fase"] == n], d) for n, d in dur.items()},
        "por_operacion": {t: resumir([f for f in medidas if f["tipo"] == t], dur_medida) for t in cfg["mezcla_operaciones"]},
        "sostenimiento_por_operacion": {t: resumir([f for f in filas if f["fase"] == "sostenimiento" and f["tipo"] == t],
                                                    dur["sostenimiento"]) for t in cfg["mezcla_operaciones"]}
        if "sostenimiento" in dur else {},
    }
    if monitor.muestras:
        def prom(campo: str, fase: str | None = None):
            v = [m[campo] for m in monitor.muestras if m.get(campo) is not None and (fase is None or m["fase"] == fase)
                 and m["fase"] not in ("espera", "fin")]
            return {"promedio": round(sum(v) / len(v), 1), "max": round(max(v), 1)} if v else None
        claves_rec = [k for k in monitor.muestras[-1] if k.endswith(("_cpu_pct", "_ram_mb")) or k == "lag_loop_max_ms"]
        resumen["recursos"] = {k: prom(k) for k in claves_rec}
        resumen["recursos_por_fase"] = {f: {k: prom(k, f) for k in claves_rec} for f in dur}

    comun.escribir_json(salida / "metadatos.json", metadatos)
    comun.escribir_json(salida / "resumen.json", resumen)
    escribir_csv(salida / "solicitudes.csv.gz", filas, comprimir=True)
    escribir_csv(salida / "recursos.csv", monitor.muestras)
    escribir_csv(salida / "serie_tiempo.csv", serie_temporal(filas))

    g = resumen["global_medido"]
    print("\n=== RESULTADO (fases medidas) ===")
    if cortes:
        print(f"[CORTE] {metadatos['corte']}")
    print(f"Solicitudes: {g['solicitudes']} | exitosas: {g['exitosas']} | error: {g['tasa_error_pct']}% {g['errores_por_tipo']}")
    print(f"Throughput: {g['throughput_ok_rps']} req/s | P50 {g['latencia_ms']['p50']} ms | P95 {g['latencia_ms']['p95']} ms | P99 {g['latencia_ms']['p99']} ms")
    print(f"Tiempo dentro de la API: P50 {g['api_ms']['p50']} ms | P95 {g['api_ms']['p95']} ms")
    print(f"Integridad: {g['integridad']}")
    print("\nPor fase:                 req/s    P50     P95   API P95")
    for n, r in resumen["por_fase"].items():
        print(f"  {n:<22}{r['throughput_ok_rps'] or 0:>7} {r['latencia_ms']['p50'] or 0:>7} {r['latencia_ms']['p95'] or 0:>7} {r['api_ms']['p95'] or 0:>7}")
    print("\nPor operación:            req    err%    P50     P95     P99   API P50")
    for t, r in resumen["por_operacion"].items():
        lm = r["latencia_ms"]
        print(f"  {t:<24}{r['solicitudes']:>6} {r['tasa_error_pct'] or 0:>6}% {lm['p50'] or 0:>7} {lm['p95'] or 0:>7} {lm['p99'] or 0:>7} {r['api_ms']['p50'] or 0:>7}")
    if "recursos" in resumen:
        r = resumen["recursos"]
        print(f"\nCPU API prom/max: {r.get('api_cpu_pct')} | CPU generador ({nproc} proc.): {r.get('generador_cpu_pct')} | lag loop: {r.get('lag_loop_max_ms')}")
    print(f"\nEvidencia: {salida.relative_to(comun.HITO_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
