"""Capa 10: cadena completa cliente HTTP -> API -> adaptador -> producto.

RF15, RF18, RF19, sección 5.5. Ejecuta las rutas principales de la API del
Hito 10 (más los endpoints de health del Hito 11) y registra para cada una:
método, path, parámetros, dependencia esperada, status HTTP, tiempo,
request ID enviado y devuelto, resumen del cuerpo, línea de log asociada e
interpretación.

Cada request envía un ``X-Request-ID`` propio (UUID) para poder buscar la
línea correspondiente en ``logs/api.stderr.log``.

Solo se usan métodos GET. El ``DELETE /sesiones`` no se ejecuta porque
modifica datos.
"""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from pathlib import Path

from common import (
    BLOQUEADA,
    FALLA,
    OK,
    REPO_ROOT,
    Config,
    Redactor,
    Resultado,
    completar_diagnostico,
    contexto_ejecucion,
    escribir_evidencia,
    imprimir_resultado,
    imprimir_resumen,
    parse_overrides,
    preparar_consola,
)


def casos(cfg: Config) -> list[dict]:
    equipo = cfg.get("MONGO_EQUIPO_DEMO", "EQ-01")
    partido = cfg.get("NEO4J_PARTIDO_DEMO", "PAR-0001")
    bucket = cfg.get("CASSANDRA_BUCKET_DEMO", "203006131800")
    sesion = cfg.get("REDIS_SESION_DEMO", "SES-API-0001")
    desde = cfg.get("INFLUX_DESDE", "2030-06-13T20:00:00Z")
    hasta = cfg.get("INFLUX_HASTA", "2030-06-13T20:01:00Z")
    iris = cfg.get("IRIS_PARTIDO_DEMO", "PAR-0001")

    return [
        # --- API y health ---
        dict(dep="API Fixture 2030", path="/health/live", params={}, esperado={200}, caso="liveness"),
        dict(dep="API Fixture 2030", path="/health/ready", params={}, esperado={200, 503}, caso="readiness"),
        dict(dep="API Fixture 2030", path="/health/dependencias", params={"refrescar": "true"}, esperado={200}, caso="diagnóstico por dependencia"),
        # --- MongoDB ---
        dict(dep="MongoDB", path=f"/api/v1/equipos/{equipo}", params={}, esperado={200}, caso="operación exitosa"),
        dict(dep="MongoDB", path="/api/v1/equipos/EQ-99", params={}, esperado={404}, caso="recurso inexistente"),
        dict(dep="MongoDB", path="/api/v1/equipos/ARG", params={}, esperado={422}, caso="error de validación"),
        dict(dep="MongoDB", path="/api/v1/jugadores", params={"equipo_codigo": equipo, "limit": 3}, esperado={200}, caso="lectura paginada"),
        # --- Neo4j ---
        dict(dep="Neo4j", path=f"/api/v1/partidos/{partido}/eventos", params={}, esperado={200}, caso="operación exitosa"),
        dict(dep="Neo4j", path="/api/v1/partidos/PAR-9999/eventos", params={}, esperado={404}, caso="recurso inexistente"),
        # --- Cassandra ---
        dict(dep="Cassandra", path=f"/api/v1/partidos/{partido}/comentarios", params={"bucket_10min": bucket, "limit": 3}, esperado={200}, caso="operación exitosa"),
        dict(dep="Cassandra", path="/api/v1/partidos/PAR-9999/comentarios", params={"bucket_10min": bucket, "limit": 3}, esperado={200}, caso="respuesta vacía válida", vacio=True),
        dict(dep="Cassandra", path=f"/api/v1/partidos/{partido}/comentarios", params={"bucket_10min": bucket[:-2] + "05"}, esperado={422}, caso="error de validación"),
        # --- Redis ---
        dict(dep="Redis", path=f"/api/v1/sesiones/{sesion}", params={}, esperado={200, 404}, caso="operación exitosa o clave ausente (200 si la sesión fue preparada; 404 si no existe o expiró)"),
        dict(dep="Redis", path="/api/v1/sesiones/SES-DIAG-INEXISTENTE", params={}, esperado={404}, caso="clave ausente"),
        # --- InfluxDB ---
        dict(dep="InfluxDB", path=f"/api/v1/partidos/{partido}/estadisticas", params={"desde": desde, "hasta": hasta, "limit": 10}, esperado={200}, caso="operación exitosa"),
        dict(dep="InfluxDB", path=f"/api/v1/partidos/{partido}/estadisticas", params={"desde": "2031-01-01T00:00:00Z", "hasta": "2031-01-01T00:01:00Z"}, esperado={200}, caso="respuesta vacía válida", vacio=True),
        dict(dep="InfluxDB", path=f"/api/v1/partidos/{partido}/estadisticas", params={"desde": hasta, "hasta": desde}, esperado={422}, caso="error de validación"),
        # --- IRIS ---
        dict(dep="InterSystems IRIS", path=f"/api/v1/partidos/{iris}/detalle", params={}, esperado={200}, caso="operación exitosa"),
        dict(dep="InterSystems IRIS", path="/api/v1/partidos/PAR-9999/detalle", params={}, esperado={404}, caso="recurso inexistente"),
    ]


def clasificar_respuesta(status: int, body: dict | None, vacio_esperado: bool) -> tuple[str, str]:
    error = (body or {}).get("error") or {}
    codigo = error.get("codigo", "")

    if status == 200:
        datos = (body or {}).get("datos")
        if isinstance(datos, list) and not datos:
            return "vacio_valido", "200 con lista vacía: ausencia válida de datos, no un error"
        return "operacion_exitosa", "200: la cadena cliente-API-adaptador-producto funcionó para este caso"
    if status == 404:
        return "recurso_inexistente", f"404 {codigo}: la dependencia respondió y el recurso no existe"
    if status == 422:
        return "error_validacion", f"422 {codigo}: rechazado por la API antes de consultar la dependencia"
    if status == 503 and codigo == "DEPENDENCIA_MAL_CONFIGURADA":
        capa = (error.get("detalles") or {}).get("capa", "?")
        return "dependencia_mal_configurada", f"503 {codigo} (capa={capa}): la dependencia respondió pero rechazó identidad/contexto"
    if status == 503:
        return "dependencia_no_disponible", f"503 {codigo}: API viva, dependencia no disponible"
    if status == 504:
        return "timeout", f"504 {codigo}: la dependencia excedió el tiempo de espera"
    if status >= 500:
        return "error_interno", f"{status} {codigo}: error interno de la API"
    return "respuesta_inesperada", f"HTTP {status}"


def resumir(body: dict | None) -> str:
    if not isinstance(body, dict):
        return "-"
    if "error" in body:
        e = body["error"]
        return f"error.codigo={e.get('codigo')}"
    partes = []
    for clave in ("estado", "estado_general", "codigo", "fuente_datos"):
        if clave in body:
            partes.append(f"{clave}={body[clave]}")
    if isinstance(body.get("datos"), list):
        partes.append(f"datos={len(body['datos'])}")
    if isinstance(body.get("eventos"), list):
        partes.append(f"eventos={len(body['eventos'])}")
    if isinstance(body.get("dependencias"), dict):
        partes.append("deps=" + ",".join(f"{k}:{v}" for k, v in body["dependencias"].items()))
    if isinstance(body.get("dependencias"), list):
        partes.append("deps=" + ",".join(f"{d['dependencia']}:{d['estado']}" for d in body["dependencias"]))
    return "; ".join(partes) or "-"


def buscar_log(log_path: Path, request_ids: list[str]) -> dict[str, list[str]]:
    encontrados: dict[str, list[str]] = {rid: [] for rid in request_ids}
    if not log_path.exists():
        return encontrados
    try:
        lineas = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-20000:]
    except Exception:
        return encontrados
    for linea in lineas:
        for rid in request_ids:
            if rid in linea:
                encontrados[rid].append(linea.strip())
    return encontrados


def evaluar(cfg: Config, redactar: Redactor) -> tuple[list[Resultado], list[dict]]:
    import httpx

    base = (cfg.get("API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")
    timeout = max(cfg.timeout, cfg.get_float("DEPENDENCY_TIMEOUT_SECONDS", 5.0) + 3)
    resultados: list[Resultado] = []
    registros: list[dict] = []
    api_caida = False

    with httpx.Client(base_url=base, timeout=timeout, trust_env=False) as http:
        for caso in casos(cfg):
            request_id = str(uuid.uuid4())
            query = "&".join(f"{k}={v}" for k, v in caso["params"].items())
            ruta = caso["path"] + (f"?{query}" if query else "")
            pregunta = f"¿La ruta responde según el contrato para el caso '{caso['caso']}'?"
            no_concluye = "Capacidad bajo carga, ni estado de rutas no ejecutadas."

            if api_caida:
                resultados.append(Resultado(
                    producto=caso["dep"], capa="api", prueba=f"GET {caso['path']} ({caso['caso']})",
                    objetivo=f"{base}{ruta}", estado=BLOQUEADA, clasificacion="bloqueada_por_capa_previa",
                    detalle="La API no es alcanzable.", cliente="httpx", origen="notebook (cliente HTTP)",
                ))
                continue

            inicio = time.perf_counter()
            try:
                r = http.get(caso["path"], params=caso["params"], headers={"X-Request-ID": request_id})
            except httpx.TimeoutException as error:
                dur = round((time.perf_counter() - inicio) * 1000, 2)
                resultados.append(completar_diagnostico(Resultado(
                    producto=caso["dep"], capa="api", prueba=f"GET {caso['path']} ({caso['caso']})",
                    objetivo=f"{base}{ruta}", estado=FALLA, clasificacion="timeout",
                    detalle=f"sin respuesta de la API en {timeout:.1f} s: {type(error).__name__}",
                    duracion_ms=dur, cliente="httpx", origen="notebook (cliente HTTP)",
                    pregunta=pregunta, no_concluye=no_concluye,
                )))
                continue
            except httpx.RequestError as error:
                dur = round((time.perf_counter() - inicio) * 1000, 2)
                api_caida = True
                resultados.append(completar_diagnostico(Resultado(
                    producto="API Fixture 2030", capa="api", prueba=f"GET {caso['path']} ({caso['caso']})",
                    objetivo=f"{base}{ruta}", estado=FALLA, clasificacion="api_no_alcanzable",
                    detalle=f"{type(error).__name__}: {error}", duracion_ms=dur,
                    cliente="httpx", origen="notebook (cliente HTTP)",
                    pregunta="¿Hay un proceso de la API escuchando en API_BASE_URL?",
                    no_concluye="Nada sobre las dependencias: la cadena se corta antes.",
                )))
                continue

            dur = round((time.perf_counter() - inicio) * 1000, 2)
            try:
                body = r.json()
            except Exception:
                body = None

            clase, interpretacion = clasificar_respuesta(r.status_code, body, caso.get("vacio", False))
            if caso.get("vacio") and clase == "operacion_exitosa":
                interpretacion += " (se esperaba vacío y llegaron datos)"

            esperado = r.status_code in caso["esperado"]
            rid_respuesta = r.headers.get("x-request-id", "")
            proceso_ms = r.headers.get("x-process-time-ms", "")

            estado = OK if esperado else FALLA
            if not esperado and clase in ("operacion_exitosa", "recurso_inexistente", "vacio_valido", "error_validacion"):
                clase = "respuesta_inesperada"

            detalle = (
                f"status={r.status_code} (esperado {sorted(caso['esperado'])}); {interpretacion}; "
                f"resumen: {resumir(body)}; X-Request-ID enviado={'igual' if rid_respuesta == request_id else rid_respuesta}; "
                f"X-Process-Time-Ms={proceso_ms}"
            )

            res = completar_diagnostico(Resultado(
                producto=caso["dep"], capa="api", prueba=f"GET {caso['path']} ({caso['caso']})",
                objetivo=f"{base}{ruta}", estado=estado, clasificacion=clase,
                detalle=redactar(detalle), duracion_ms=dur, cliente=f"httpx -> API -> adaptador {caso['dep']}",
                origen="notebook (cliente HTTP)", pregunta=pregunta, no_concluye=no_concluye,
            ))
            resultados.append(res)
            registros.append({
                "metodo": "GET",
                "path": caso["path"],
                "parametros": caso["params"],
                "caso": caso["caso"],
                "dependencia_esperada": caso["dep"],
                "status": r.status_code,
                "status_esperado": sorted(caso["esperado"]),
                "tiempo_cliente_ms": dur,
                "x_process_time_ms": proceso_ms,
                "request_id": request_id,
                "request_id_devuelto_igual": rid_respuesta == request_id,
                "resumen": resumir(body),
                "clasificacion": clase,
                "interpretacion": interpretacion,
            })

    # Logs asociados (RF19, RNF11)
    log_path = (REPO_ROOT / (cfg.get("API_LOG_FILE") or "logs/api.stderr.log")).resolve()
    time.sleep(0.3)
    logs = buscar_log(log_path, [reg["request_id"] for reg in registros])
    for reg in registros:
        lineas = logs.get(reg["request_id"], [])
        reg["log_asociado"] = [redactar(l) for l in lineas[-3:]] or [
            f"(sin línea en {log_path.name}: ¿la API se inició con scripts/reiniciar_api.ps1?)"
        ]

    return resultados, registros


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(description="Hito 11 - pruebas de la API integrada")
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR")
    parser.add_argument("--etiqueta", default="")
    args = parser.parse_args(argv)

    cfg = Config(parse_overrides(args.set))
    redactar = Redactor(cfg.secretos())
    contexto = contexto_ejecucion(cfg, "api")
    contexto["api_base_url"] = cfg.get("API_BASE_URL")

    print("=== HITO 11 - CADENA CLIENTE HTTP -> API -> ADAPTADOR -> PRODUCTO ===")
    print(f"Fecha: {contexto['fecha']} | API: {contexto['api_base_url']}")
    print()

    resultados, registros = evaluar(cfg, redactar)
    for r in resultados:
        imprimir_resultado(r)

    print()
    print("=== LOGS ASOCIADOS (por request_id) ===")
    for reg in registros:
        print(f"{reg['status']} GET {reg['path']} request_id={reg['request_id']}")
        for linea in reg["log_asociado"]:
            print(f"    {linea[:220]}")

    imprimir_resumen(resultados)
    txt, _ = escribir_evidencia(
        "resultados_api", contexto, resultados, redactar, args.etiqueta,
        extra={"solicitudes": registros},
    )
    print(f"\nEvidencia: {txt}")
    return 1 if any(r.estado == FALLA for r in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())
