"""PRUEBA DE LA HIPÓTESIS (RF7): ¿dónde se va el tiempo del endpoint de IRIS?

Mide directamente contra IRIS, SIN pasar por la API:
  A) patrón actual del adaptador: conectar -> consultar -> cerrar, en cada operación.
  B) patrón con conexión reutilizada: un pool chico de conexiones abiertas que se comparten.
  C) capacidad de licencias: cuántas conexiones simultáneas acepta IRIS Community antes de
     responder "Unable to allocate a license" (define el tamaño máximo razonable del pool).
Cada patrón se corre secuencial (1 hilo) y concurrente (N hilos), separando el tiempo de
connect() del tiempo de las consultas. Si connect() domina, la hipótesis se confirma.

Uso:  python diagnostico_iris.py [operaciones=200] [hilos=20] [pool=5]
"""
from __future__ import annotations

import json
import queue
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import comun

import iris.dbapi as iris_dbapi

S = comun.get_settings()
CODIGO = "PAR-DEMO"
SQL = ("SELECT ID, Codigo, FechaHora, EquipoLocalId, EquipoVisitanteId, Estado, ArbitroPrincipal "
       "FROM Fixture.Partido WHERE Codigo = ?")
SQL_EV = "SELECT ID, Tipo, Minuto, Detalle FROM Fixture.EventoPartido WHERE Partido = ? ORDER BY Minuto, ID"


def conectar():
    return iris_dbapi.connect(S.iris_host, S.iris_port, S.iris_namespace, S.iris_username,
                              S.iris_password.get_secret_value())


def consultar(con) -> None:
    cur = con.cursor()
    cur.execute(SQL, [CODIGO])
    fila = cur.fetchall()
    if fila:
        cur.execute(SQL_EV, [fila[0][0]])
        cur.fetchall()
    cur.close()


def op_por_solicitud() -> tuple[float, float]:
    t0 = time.perf_counter()
    con = conectar()
    t1 = time.perf_counter()
    consultar(con)
    t2 = time.perf_counter()
    con.close()
    return (t1 - t0) * 1000, (t2 - t1) * 1000


def correr(nombre: str, ops: int, hilos: int, reutilizar: bool, pool_size: int = 1) -> dict:
    conn_ms, query_ms, total_ms, errores = [], [], [], Counter()
    pool: queue.Queue = queue.Queue()
    if reutilizar:
        try:
            for _ in range(pool_size):
                pool.put(conectar())
        except Exception as error:  # noqa: BLE001
            print(f"  {nombre:<38} no se pudo armar el pool de {pool_size}: {type(error).__name__}")
            while not pool.empty():
                pool.get().close()
            return {"escenario": nombre, "error_pool": str(error)[:200]}

    def una(_):
        t = time.perf_counter()
        try:
            if reutilizar:
                con = pool.get()
                try:
                    t1 = time.perf_counter()
                    consultar(con)
                    q = (time.perf_counter() - t1) * 1000
                finally:
                    pool.put(con)
                c = 0.0
            else:
                c, q = op_por_solicitud()
            return c, q, (time.perf_counter() - t) * 1000, None
        except Exception as error:  # noqa: BLE001
            return None, None, (time.perf_counter() - t) * 1000, type(error).__name__

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        for c, q, tot, err in ex.map(una, range(ops)):
            if err:
                errores[err] += 1
                continue
            conn_ms.append(c)
            query_ms.append(q)
            total_ms.append(tot)
    duracion = time.perf_counter() - inicio
    while not pool.empty():
        pool.get().close()

    def p95(v):
        return round(sorted(v)[int(0.95 * (len(v) - 1))], 2) if v else None
    r = {
        "escenario": nombre, "operaciones": ops, "hilos": hilos, "exitosas": len(total_ms),
        "errores": dict(errores), "ops_por_s": round(len(total_ms) / duracion, 1),
        "connect_ms_prom": round(statistics.mean(conn_ms), 2) if conn_ms else None,
        "consulta_ms_prom": round(statistics.mean(query_ms), 2) if query_ms else None,
        "total_ms_p50": round(statistics.median(total_ms), 2) if total_ms else None,
        "total_ms_p95": p95(total_ms),
    }
    print(f"  {nombre:<38} ok {r['exitosas']:>4}/{ops}  {r['ops_por_s']:>7} ops/s  connect {r['connect_ms_prom']} ms"
          f"  consulta {r['consulta_ms_prom']} ms  P50 {r['total_ms_p50']}  P95 {r['total_ms_p95']}  err {r['errores'] or '-'}")
    return r


from collections import Counter  # noqa: E402


def capacidad_licencias(maximo: int = 30) -> dict:
    """Abre conexiones de a una (sin cerrarlas) hasta que IRIS rechaza o se llega al máximo."""
    abiertas, error = [], None
    for _ in range(maximo):
        try:
            abiertas.append(conectar())
        except Exception as exc:  # noqa: BLE001
            error = str(exc).split("Details:")[-1].strip()[:120]
            break
    n = len(abiertas)
    for con in abiertas:
        try:
            con.close()
        except Exception:  # noqa: BLE001
            pass
    print(f"  C  conexiones simultaneas aceptadas por IRIS: {n} (tope de la prueba {maximo})"
          + (f" -> rechazo: {error}" if error else ""))
    return {"conexiones_simultaneas_aceptadas": n, "tope_probado": maximo, "rechazo": error,
            "nota": "medido con la API levantada (que tambien puede usar conexiones)"}


def main() -> int:
    ops = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    hilos = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    pool_size = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    print("=== HITO 12 - DIAGNÓSTICO IRIS (directo al motor, sin API) ===")
    print(f"Fecha: {comun.ahora_iso()} | operaciones {ops} | hilos concurrentes {hilos}")
    consultar_con = conectar()   # calentamiento
    consultar(consultar_con)
    consultar_con.close()
    resultados = [
        correr("A1 conexion por operacion, 1 hilo", ops, 1, False),
        correr("B1 conexion reutilizada, 1 hilo", ops, 1, True, 1),
        correr(f"A{hilos} conexion por operacion, {hilos} hilos", ops, hilos, False),
        correr(f"B{hilos} pool de {pool_size} conexiones, {hilos} hilos", ops, hilos, True, pool_size),
    ]
    time.sleep(2)
    licencias = capacidad_licencias()
    comun.escribir_json(comun.EVIDENCIA_DIR / "diagnostico_iris.json",
                        {"fecha": comun.ahora_iso(), "hardware": comun.info_hardware(), "pool_size": pool_size,
                         "resultados": resultados, "licencias": licencias})
    print("Evidencia: docs/evidencia/diagnostico_iris.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
