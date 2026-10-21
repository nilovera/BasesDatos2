"""Capa 1: configuración (RF3).

Verifica que cada producto tenga las variables necesarias, muestra de dónde
sale cada valor y qué host/puerto/contexto se usará, sin imprimir nunca
passwords ni tokens. También comprueba que los archivos con secretos estén
fuera de Git y advierte cuando ``localhost`` se usaría desde un contenedor.

Uso independiente:
    .venv\\Scripts\\python.exe hito11-conectividad\\scripts\\prueba_config.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from common import (
    ADVERTENCIA,
    CONFIG_API,
    CONFIG_LOCAL,
    FALLA,
    OK,
    PRODUCTOS,
    REPO_ROOT,
    Config,
    Redactor,
    Resultado,
    completar_diagnostico,
    contexto_ejecucion,
    en_contenedor,
    escribir_evidencia,
    host_port_from_url,
    imprimir_resultado,
    imprimir_resumen,
    parse_overrides,
    preparar_consola,
)


def destino_producto(cfg: Config, clave: str) -> tuple[str, str, str]:
    """(host:puerto, protocolo, contexto) tal como los usará la API."""
    if clave == "mongodb":
        return (
            f"{cfg.get('MONGODB_HOST')}:{cfg.get('MONGODB_PORT')}",
            "MongoDB Wire Protocol (TCP)",
            f"database={cfg.get('MONGODB_DATABASE')}; authSource={cfg.get('MONGODB_AUTH_SOURCE')}",
        )
    if clave == "neo4j":
        host, port = host_port_from_url(cfg.get("NEO4J_URI", "bolt://127.0.0.1:7687"), 7687)
        http_host, http_port = host_port_from_url(cfg.get("NEO4J_HTTP_URL"), 7474)
        return (
            f"{host}:{port} (Bolt) / {http_host}:{http_port} (HTTP Browser)",
            "Bolt (aplicación) y HTTP (portal)",
            f"database={cfg.get('NEO4J_DATABASE')}",
        )
    if clave == "cassandra":
        return (
            f"{cfg.get('CASSANDRA_HOSTS')}:{cfg.get('CASSANDRA_PORT')}",
            "CQL native protocol (TCP)",
            f"keyspace={cfg.get('CASSANDRA_KEYSPACE')}; tabla={cfg.get('CASSANDRA_TABLA')}",
        )
    if clave == "redis":
        return (
            f"{cfg.get('REDIS_HOST')}:{cfg.get('REDIS_PORT')}",
            "RESP (TCP)",
            f"db={cfg.get('REDIS_DATABASE')}; claves sesion:*",
        )
    if clave == "influxdb":
        host, port = host_port_from_url(cfg.get("INFLUXDB_URL", "http://127.0.0.1:8181"), 8181)
        return (
            f"{host}:{port}",
            "HTTP API v3 (/health, /api/v3/query_sql)",
            f"databases={cfg.get('INFLUXDB_DETAIL_DATABASE')}, {cfg.get('INFLUXDB_HISTORICAL_DATABASE')}",
        )
    if clave == "iris":
        return (
            f"{cfg.get('IRIS_HOST')}:{cfg.get('IRIS_PORT')} (Superserver) / "
            f"{cfg.get('IRIS_HOST')}:{cfg.get('IRIS_PORTAL_PORT')} (portal HTTP)",
            "Superserver (DB-API) y HTTP (portal)",
            f"namespace={cfg.get('IRIS_NAMESPACE')}",
        )
    return ("-", "-", "-")


def mecanismo_auth(cfg: Config, clave: str) -> str:
    def estado(var: str) -> str:
        return "presente (valor oculto)" if cfg.definida(var) else "AUSENTE"

    # Nota: se evita escribir "password:" o "token=" seguidos de texto para
    # no confundir al redactor de secretos.

    if clave == "mongodb":
        return f"SCRAM con usuario {estado('MONGODB_USERNAME')} y password {estado('MONGODB_PASSWORD')}"
    if clave == "neo4j":
        return f"basic auth Bolt con usuario {estado('NEO4J_USERNAME')} y password {estado('NEO4J_PASSWORD')}"
    if clave == "cassandra":
        if cfg.definida("CASSANDRA_USERNAME"):
            return f"PlainText con usuario definido y password {estado('CASSANDRA_PASSWORD')}"
        return "sin credenciales configuradas (el laboratorio usa AllowAllAuthenticator)"
    if clave == "redis":
        if cfg.definida("REDIS_PASSWORD"):
            return "AUTH con password (valor oculto)"
        return "sin password configurada (requirepass vacío en el laboratorio)"
    if clave == "influxdb":
        return f"token Bearer {estado('INFLUXDB_TOKEN')}"
    if clave == "iris":
        return f"usuario {estado('IRIS_USERNAME')} y password {estado('IRIS_PASSWORD')}"
    return "-"


def evaluar(cfg: Config, productos: list[str], redactar: Redactor) -> list[Resultado]:
    resultados: list[Resultado] = []
    dentro_contenedor = en_contenedor()

    for clave in productos:
        spec = PRODUCTOS[clave]
        faltantes = [var for var in spec["requeridas"] if not cfg.definida(var)]
        destino, protocolo, contexto = destino_producto(cfg, clave)
        origenes = sorted({cfg.origen(var) for var in spec["requeridas"]})

        detalle = (
            f"destino={destino}; protocolo={protocolo}; {contexto}; "
            f"autenticacion={mecanismo_auth(cfg, clave)}; origen de valores={', '.join(origenes)}"
        )

        if faltantes:
            resultados.append(
                completar_diagnostico(
                    Resultado(
                        producto=spec["nombre"],
                        capa="configuracion",
                        prueba="variables requeridas presentes",
                        objetivo=destino,
                        estado=FALLA,
                        clasificacion="variables_faltantes",
                        detalle=f"faltan: {', '.join(faltantes)}. {detalle}",
                        cliente="lectura de configuración",
                        pregunta="¿El entorno sabe a qué host, puerto y contexto conectarse y con qué identidad?",
                        no_concluye="Nada sobre la red ni el servidor: solo que la configuración está incompleta.",
                    )
                )
            )
        else:
            resultados.append(
                Resultado(
                    producto=spec["nombre"],
                    capa="configuracion",
                    prueba="variables requeridas presentes",
                    objetivo=destino,
                    estado=OK,
                    clasificacion="configuracion_completa",
                    detalle=detalle,
                    cliente="lectura de configuración",
                    pregunta="¿El entorno sabe a qué host, puerto y contexto conectarse y con qué identidad?",
                    no_concluye="Que el host exista, que el puerto esté abierto o que la credencial sea válida.",
                )
            )

        # RNF3: localhost no significa lo mismo dentro de un contenedor.
        host_vars = [v for v in spec["requeridas"] if v.endswith(("_HOST", "_HOSTS", "_URI", "_URL"))]
        usa_localhost = any(
            (cfg.get(v) or "").find(t) >= 0
            for v in host_vars
            for t in ("localhost", "127.0.0.1")
        )
        if dentro_contenedor and usa_localhost:
            resultados.append(
                completar_diagnostico(
                    Resultado(
                        producto=spec["nombre"],
                        capa="configuracion",
                        prueba="localhost desde contenedor",
                        objetivo=destino,
                        estado=ADVERTENCIA,
                        clasificacion="host_no_resuelto",
                        detalle=(
                            "El diagnóstico corre dentro de un contenedor y la configuración usa localhost/127.0.0.1: "
                            "apunta al propio contenedor, no a la notebook ni al contenedor del producto."
                        ),
                        cliente="lectura de configuración",
                        requerida=False,
                        pregunta="¿El host configurado tiene sentido desde el origen real de la conexión?",
                        no_concluye="Que la conexión falle: solo advierte un riesgo de entorno equivocado.",
                    )
                )
            )

    # RNF7: los archivos con secretos no deben estar versionados.
    for archivo in (CONFIG_API, CONFIG_LOCAL):
        if not archivo.exists():
            continue
        relativo = archivo.relative_to(REPO_ROOT).as_posix()
        try:
            ignorado = subprocess.run(
                ["git", "check-ignore", "-q", relativo],
                cwd=REPO_ROOT,
                capture_output=True,
                timeout=5,
            ).returncode == 0
            versionado = subprocess.run(
                ["git", "ls-files", "--error-unmatch", relativo],
                cwd=REPO_ROOT,
                capture_output=True,
                timeout=5,
            ).returncode == 0
        except Exception:
            continue

        ok = ignorado and not versionado
        resultados.append(
            completar_diagnostico(
                Resultado(
                    producto="Repositorio",
                    capa="configuracion",
                    prueba=f"{relativo} fuera de Git",
                    objetivo=relativo,
                    estado=OK if ok else FALLA,
                    clasificacion="secretos_no_versionados" if ok else "secreto_versionado",
                    detalle=(
                        "ignorado por .gitignore y no versionado" if ok else
                        f"ignorado={ignorado}, versionado={versionado}: quitarlo del índice con 'git rm --cached'"
                    ),
                    cliente="git check-ignore / git ls-files",
                    requerida=False,
                    pregunta="¿Las credenciales locales quedan fuera del repositorio?",
                    no_concluye="Que no existan secretos en otros archivos o en el historial.",
                    hipotesis="" if ok else "El archivo con credenciales quedó agregado al repositorio.",
                    siguiente_paso="" if ok else "git rm --cached <archivo>, rotar las credenciales y verificar .gitignore.",
                )
            )
        )

    return resultados


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(description="Hito 11 - verificación de configuración")
    parser.add_argument("--producto", default="todos", choices=["todos", *PRODUCTOS])
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR")
    parser.add_argument("--etiqueta", default="")
    args = parser.parse_args(argv)

    cfg = Config(parse_overrides(args.set))
    redactar = Redactor(cfg.secretos())
    productos = list(PRODUCTOS) if args.producto == "todos" else [args.producto]

    contexto = contexto_ejecucion(cfg, "configuracion")
    print("=== HITO 11 - CAPA DE CONFIGURACION ===")
    print(f"Fecha: {contexto['fecha']} | Entorno: {contexto['entorno']} | Commit: {contexto['commit']}")
    print()

    resultados = evaluar(cfg, productos, redactar)
    for r in resultados:
        imprimir_resultado(r)
    imprimir_resumen(resultados)

    txt, _ = escribir_evidencia("resultados_config", contexto, resultados, redactar, args.etiqueta)
    print(f"\nEvidencia: {txt}")
    return 1 if any(r.estado == FALLA and r.requerida for r in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())
