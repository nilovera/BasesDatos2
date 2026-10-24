"""PREPARACIÓN del Hito 12.

1. Genera datos sintéticos propios del hito (no toca datos de otros hitos):
   - Redis: sesiones  sesion:SES-H12-0001 ... (TTL largo para que duren toda la prueba).
   - IRIS : partidos  PAR-H12001 ... con eventos (para que la carga no lea siempre la misma fila).
   - Cassandra: 25 comentarios por bucket de 10 min en los 96 partidos (28.800 comentarios, en las
     dos tablas del Hito 6), con UUID deterministas marcados como "sintético H12".
   Es idempotente: si ya existen, no se duplican.
2. Releva, a través de la API y con concurrencia 1, qué claves existen en cada base y guarda
   la "huella" (hash) de cada respuesta correcta en datos-o-generadores/catalogo_claves.json.
   Durante la carga, cada respuesta se compara con esta huella -> validación de integridad.

Uso (desde la carpeta de la API, con la API levantada):
    .\\.venv\\Scripts\\python.exe fixture2030-hito-12-carga-optimizacion\\scripts\\preparar_datos.py
"""
from __future__ import annotations

import random
import sys
import time
from collections import Counter
from datetime import datetime, timedelta

import httpx

import comun

cfg = comun.cargar_config()
SINT = cfg["datos_sinteticos"]
rng = random.Random(cfg["semilla"])

EQUIPOS_3 = ["ARG", "BRA", "URU", "ESP", "POR", "MAR", "FRA", "ALE", "ITA", "ING", "MEX", "USA",
             "JAP", "COR", "SEN", "NED", "CRO", "BEL", "COL", "CHI"]
TIPOS_EVENTO = ["Gol", "Tarjeta amarilla", "Tarjeta roja", "Cambio", "Penal", "Corner", "Offside"]


# ---------------------------------------------------------------- 1a. Redis
def preparar_redis() -> int:
    import redis
    s = comun.get_settings()
    cliente = redis.Redis(host=s.redis_host, port=s.redis_port, db=s.redis_database, decode_responses=True)
    pipe = cliente.pipeline(transaction=False)
    for i in range(1, SINT["sesiones_redis"] + 1):
        sid = f"{comun.PREFIJO_SESION_REDIS}{i:04d}"
        clave = f"sesion:{sid}"
        pipe.hset(clave, mapping={
            "sesion_id": sid,
            "usuario_id": f"USR-{rng.randint(1, 5000):04d}",
            "rol": "moderador" if i % 25 == 0 else "fan",
            "ultimo_acceso": "2030-06-13T19:00:00Z",   # fijo -> respuesta determinista
            "estado": "activa",
            "partido_actual": f"PAR-{rng.randint(1, 96):04d}",
            "acciones": str(rng.randint(0, 40)),
        })
        pipe.expire(clave, SINT["ttl_sesiones_s"])
    pipe.execute()
    total = sum(1 for _ in cliente.scan_iter(match=f"sesion:{comun.PREFIJO_SESION_REDIS}*", count=500))
    cliente.close()
    return total


# ---------------------------------------------------------------- 1b. IRIS
def preparar_iris() -> tuple[int, int]:
    import iris.dbapi as iris_dbapi
    s = comun.get_settings()
    con = iris_dbapi.connect(s.iris_host, s.iris_port, s.iris_namespace, s.iris_username,
                             s.iris_password.get_secret_value())
    cur = con.cursor()
    cur.execute("SELECT TOP 1 ID FROM Fixture.Arbitro ORDER BY ID")
    fila = cur.fetchall()
    arbitro_id = fila[0][0] if fila else None

    base = datetime(2030, 6, 13, 16, 0, 0)
    creados = 0
    for i in range(1, SINT["partidos_iris"] + 1):
        codigo = f"{comun.PREFIJO_PARTIDO_IRIS}{i:03d}"
        cur.execute("SELECT ID FROM Fixture.Partido WHERE Codigo = ?", [codigo])
        if cur.fetchall():
            continue  # ya existe -> idempotente
        local, visitante = rng.sample(EQUIPOS_3, 2)
        fecha = base + timedelta(days=(i - 1) // 4, hours=3 * ((i - 1) % 4))
        cur.execute(
            "INSERT INTO Fixture.Partido (Codigo, FechaHora, EquipoLocalId, EquipoVisitanteId, Estado, ArbitroPrincipal) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [codigo, fecha.strftime("%Y-%m-%d %H:%M:%S"), local, visitante, "Finalizado", arbitro_id],
        )
        cur.execute("SELECT ID FROM Fixture.Partido WHERE Codigo = ?", [codigo])
        partido_id = cur.fetchall()[0][0]
        minimo, maximo = SINT["eventos_por_partido_iris"]
        for minuto in sorted(rng.sample(range(1, 95), rng.randint(minimo, maximo))):
            tipo = rng.choice(TIPOS_EVENTO)
            cur.execute(
                "INSERT INTO Fixture.EventoPartido (Partido, Tipo, Minuto, Detalle) VALUES (?, ?, ?, ?)",
                [partido_id, tipo, minuto, f"{tipo} sintético Hito 12"],
            )
        creados += 1
    try:
        con.commit()
    except Exception:  # noqa: BLE001  (si la conexión es autocommit no hace falta)
        pass
    cur.execute(f"SELECT COUNT(*) FROM Fixture.Partido WHERE Codigo %STARTSWITH '{comun.PREFIJO_PARTIDO_IRIS}'")
    total = cur.fetchall()[0][0]
    cur.close()
    con.close()
    return creados, total


# ---------------------------------------------------------------- 1c. Cassandra
def preparar_cassandra() -> int:
    from cassandra.concurrent import execute_concurrent_with_args
    cluster, ses = comun.sesion_cassandra()
    cols = "creado_en, comentario_id, usuario_nombre, contenido, estado_moderacion, likes"
    ins_p = ses.prepare(f"INSERT INTO comentarios_por_partido (partido_id, bucket_10min, {cols}, usuario_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
    ins_u = ses.prepare(f"INSERT INTO comentarios_por_usuario (usuario_id, bucket_dia, {cols}, partido_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
    args_p, args_u = [], []
    for c in comun.comentarios_sinteticos(SINT["comentarios_por_bucket_cassandra"], cfg["semilla"]):
        comunes = (c["creado_en"], c["comentario_id"], c["usuario_nombre"], c["contenido"],
                   c["estado_moderacion"], c["likes"])
        args_p.append((c["partido_id"], c["bucket_10min"], *comunes, c["usuario_id"]))
        args_u.append((c["usuario_id"], c["bucket_dia"], *comunes, c["partido_id"]))
    fallas = 0
    for stmt, args in ((ins_p, args_p), (ins_u, args_u)):
        for ok, _ in execute_concurrent_with_args(ses, stmt, args, concurrency=64, raise_on_first_error=False):
            fallas += 0 if ok else 1
    cluster.shutdown()
    if fallas:
        print(f"   [AVISO] {fallas} inserciones fallidas en Cassandra")
    return len(args_p)


# ---------------------------------------------------------------- 2. Relevamiento por la API
def candidatos() -> list[dict]:
    c: list[dict] = []
    for n in range(1, 65):
        c.append({"tipo": "equipo_mongodb", "motor": "MongoDB", "clave": f"EQ-{n:02d}",
                  "partido": None, "url": f"/api/v1/equipos/EQ-{n:02d}"})
    for n in range(1, 97):
        p = f"PAR-{n:04d}"
        c.append({"tipo": "eventos_neo4j", "motor": "Neo4j", "clave": p, "partido": p,
                  "url": f"/api/v1/partidos/{p}/eventos"})
    # Cassandra: misma regla que el generador del Hito 6 (8 partidos por día, 120 min desde las 18:00)
    for n in range(1, 97):
        p = f"PAR-{n:04d}"
        dia = datetime(2030, 6, 13) + timedelta(days=(n - 1) // 8)
        buckets = [dia.replace(hour=18) + timedelta(minutes=10 * k) for k in range(12)]
        if n == 1:
            buckets += [dia.replace(hour=20), dia.replace(hour=20, minute=10)]
        for b in buckets:
            bucket = b.strftime("%Y%m%d%H%M")
            c.append({"tipo": "comentarios_cassandra", "motor": "Cassandra", "clave": f"{p}@{bucket}",
                      "partido": p, "url": f"/api/v1/partidos/{p}/comentarios?bucket_10min={bucket}&limit=20"})
    inicio = datetime(2030, 6, 13, 20, 0, 0)
    for m in range(90):
        d = (inicio + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")
        h = (inicio + timedelta(minutes=m + 1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for eq in ("ARG", "MEX"):
            c.append({"tipo": "estadisticas_influxdb", "motor": "InfluxDB", "clave": f"PAR-0001@{eq}@{d}",
                      "partido": "PAR-0001",
                      "url": f"/api/v1/partidos/PAR-0001/estadisticas?desde={d}&hasta={h}"
                             f"&granularidad=detalle&equipo_id={eq}&limit=10"})
    for i in range(1, SINT["sesiones_redis"] + 1):
        sid = f"{comun.PREFIJO_SESION_REDIS}{i:04d}"
        c.append({"tipo": "sesion_redis", "motor": "Redis", "clave": sid, "partido": None,
                  "url": f"/api/v1/sesiones/{sid}"})
    iris_codigos = ["PAR-DEMO"] + [f"PAR-{n:04d}" for n in range(1, 11)] + \
                   [f"{comun.PREFIJO_PARTIDO_IRIS}{i:03d}" for i in range(1, SINT["partidos_iris"] + 1)]
    for p in iris_codigos:
        c.append({"tipo": "detalle_iris", "motor": "InterSystems IRIS", "clave": p, "partido": p,
                  "url": f"/api/v1/partidos/{p}/detalle"})
    return c


def contar_elementos(cuerpo: dict) -> int:
    for campo in ("datos", "eventos"):
        if isinstance(cuerpo.get(campo), list):
            return len(cuerpo[campo])
    return 1


def relevar(base_url: str) -> list[dict]:
    catalogo = []
    lista = candidatos()
    with httpx.Client(base_url=base_url, timeout=30) as cliente:
        for n, cand in enumerate(lista, 1):
            r1 = cliente.get(cand["url"])
            if r1.status_code != 200:
                continue
            cuerpo = r1.json()
            elementos = contar_elementos(cuerpo)
            if elementos == 0:
                continue  # clave sin datos: no aporta a la prueba
            r2 = cliente.get(cand["url"])
            h1 = comun.huella(cuerpo)
            h2 = comun.huella(r2.json()) if r2.status_code == 200 else "error"
            catalogo.append({**cand, "huella": h1, "determinista": h1 == h2, "elementos": elementos})
            if n % 200 == 0:
                print(f"   relevadas {n}/{len(lista)} claves candidatas...")
    return catalogo


def main() -> int:
    print("=== HITO 12 - PREPARAR DATOS ===")
    print(f"Fecha: {comun.ahora_iso()}")
    base_url = cfg["api_base_url"]
    try:
        httpx.get(f"{base_url}/health", timeout=5).raise_for_status()
    except Exception as error:  # noqa: BLE001
        print(f"[ERROR] La API no responde en {base_url}: {type(error).__name__}. Levantarla con scripts\\reiniciar_api.ps1")
        return 1

    t0 = time.perf_counter()
    print("\n1) Redis: sesiones sintéticas")
    total_ses = preparar_redis()
    print(f"   sesiones SES-H12-* presentes: {total_ses}")

    print("\n2) IRIS: partidos sintéticos")
    try:
        creados, total_par = preparar_iris()
        print(f"   creados ahora: {creados} | PAR-H12* presentes: {total_par}")
    except Exception as error:  # noqa: BLE001
        print(f"   [AVISO] No se pudieron crear partidos en IRIS ({type(error).__name__}: {error}).")
        print("   La prueba sigue con los partidos existentes en IRIS.")
        creados, total_par = 0, 0

    print("\n3) Cassandra: comentarios sintéticos (upsert, no duplica)")
    try:
        total_com = preparar_cassandra()
        print(f"   comentarios H12 escritos (por tabla): {total_com}")
    except Exception as error:  # noqa: BLE001
        print(f"   [AVISO] No se pudieron cargar comentarios ({type(error).__name__}: {error}).")
        total_com = 0

    print("\n4) Relevamiento de claves por la API (concurrencia 1, doble lectura)")
    catalogo = relevar(base_url)
    por_tipo = Counter(e["tipo"] for e in catalogo)
    no_det = Counter(e["tipo"] for e in catalogo if not e["determinista"])
    elementos = Counter()
    for e in catalogo:
        elementos[e["tipo"]] += e["elementos"]

    resumen = {
        "fecha": comun.ahora_iso(),
        "semilla": cfg["semilla"],
        "sesiones_redis_sinteticas": total_ses,
        "partidos_iris_sinteticos": total_par,
        "comentarios_cassandra_sinteticos_por_tabla": total_com,
        "claves_por_tipo": dict(por_tipo),
        "elementos_devueltos_por_tipo": dict(elementos),
        "claves_no_deterministas": dict(no_det),
        "total_claves": len(catalogo),
        "duracion_s": round(time.perf_counter() - t0, 1),
    }
    comun.escribir_json(comun.CATALOGO_PATH, {"resumen": resumen, "claves": catalogo})
    comun.escribir_json(comun.EVIDENCIA_DIR / "preparacion_datos.json", resumen)

    print("\n=== CLAVES DISPONIBLES PARA LA CARGA ===")
    for tipo, n in sorted(por_tipo.items()):
        print(f"   {tipo:<24} {n:>5} claves  ({elementos[tipo]} elementos)  no deterministas: {no_det.get(tipo, 0)}")
    print(f"   TOTAL {len(catalogo)} claves en {resumen['duracion_s']} s")
    faltan = [t for t in cfg["mezcla_operaciones"] if por_tipo.get(t, 0) == 0]
    if faltan:
        print(f"\n[ERROR] Sin claves válidas para: {', '.join(faltan)}. Revisar que esa base tenga sus datos cargados.")
        return 1
    print(f"\nCatálogo: {comun.CATALOGO_PATH.relative_to(comun.HITO_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
