"""Capas 2 a 4: proceso (contenedor), resolución de host y conexión TCP.

RF4, RF5, RNF3. Para cada puerto que usa la API se ejecuta, desde el mismo
entorno que la API (la notebook):

1. estado del contenedor según Docker (informativo: un contenedor
   "running" NO prueba que la dependencia esté disponible);
2. resolución del nombre configurado (getaddrinfo);
3. apertura de un socket TCP con timeout acotado.

Una conexión TCP exitosa solo prueba que existe un listener en host:puerto.
No prueba protocolo, autenticación, autorización, contexto ni consultas.

Opcional ``--desde-contenedor <nombre>``: repite la prueba TCP desde dentro
de un contenedor (con bash /dev/tcp) contra 127.0.0.1 y
host.docker.internal, para mostrar que "localhost" no significa lo mismo
en la notebook y dentro de un contenedor.
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time

from common import (
    ADVERTENCIA,
    BLOQUEADA,
    FALLA,
    OK,
    PRODUCTOS,
    SKIP,
    Config,
    Redactor,
    Resultado,
    clasificar_error_red,
    completar_diagnostico,
    contexto_ejecucion,
    docker_contenedores,
    docker_disponible,
    escribir_evidencia,
    host_port_from_url,
    imprimir_resultado,
    imprimir_resumen,
    parse_overrides,
    preparar_consola,
    resolver_contenedor,
)


def objetivos(cfg: Config, productos: list[str], incluir_api: bool) -> list[dict]:
    """Lista de (producto, descripcion, host, puerto, requerido)."""
    lista = []

    def agregar(clave, descripcion, host, port, requerido=True, protocolo=""):
        lista.append(
            {
                "producto": PRODUCTOS[clave]["nombre"] if clave in PRODUCTOS else clave,
                "clave": clave,
                "descripcion": descripcion,
                "host": host,
                "port": int(port),
                "requerido": requerido,
                "protocolo": protocolo,
            }
        )

    if "mongodb" in productos:
        agregar("mongodb", "puerto MongoDB", cfg.get("MONGODB_HOST", "127.0.0.1"),
                cfg.get_int("MONGODB_PORT", 27017), protocolo="MongoDB wire")
    if "neo4j" in productos:
        host, port = host_port_from_url(cfg.get("NEO4J_URI", "bolt://127.0.0.1:7687"), 7687)
        agregar("neo4j", "puerto Bolt (usado por la API)", host, port, protocolo="Bolt")
        host, port = host_port_from_url(cfg.get("NEO4J_HTTP_URL"), 7474)
        agregar("neo4j", "puerto HTTP Browser (no usado por la API)", host, port,
                requerido=False, protocolo="HTTP")
    if "cassandra" in productos:
        port = cfg.get_int("CASSANDRA_PORT", 9042)
        for host in (cfg.get("CASSANDRA_HOSTS", "127.0.0.1") or "").split(","):
            if host.strip():
                agregar("cassandra", "puerto CQL", host.strip(), port, protocolo="CQL")
    if "redis" in productos:
        agregar("redis", "puerto RESP", cfg.get("REDIS_HOST", "127.0.0.1"),
                cfg.get_int("REDIS_PORT", 6379), protocolo="RESP")
    if "influxdb" in productos:
        host, port = host_port_from_url(cfg.get("INFLUXDB_URL", "http://127.0.0.1:8181"), 8181)
        agregar("influxdb", "puerto HTTP API v3", host, port, protocolo="HTTP")
    if "iris" in productos:
        agregar("iris", "Superserver (usado por la API)", cfg.get("IRIS_HOST", "127.0.0.1"),
                cfg.get_int("IRIS_PORT", 1972), protocolo="Superserver")
        agregar("iris", "portal HTTP (no usado por la API)", cfg.get("IRIS_HOST", "127.0.0.1"),
                cfg.get_int("IRIS_PORTAL_PORT", 52773), requerido=False, protocolo="HTTP")
    if incluir_api:
        host, port = host_port_from_url(cfg.get("API_BASE_URL"), 8000)
        lista.append(
            {
                "producto": "API Fixture 2030",
                "clave": "api",
                "descripcion": "puerto de la API (uvicorn)",
                "host": host,
                "port": port,
                "requerido": True,
                "protocolo": "HTTP",
            }
        )
    return lista


def probar_resolucion(host: str, timeout: float) -> tuple[str, str, str, list[str]]:
    socket.setdefaulttimeout(timeout)
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    finally:
        socket.setdefaulttimeout(None)
    direcciones = sorted({info[4][0] for info in infos})
    return OK, "host_resuelto", f"{host} -> {', '.join(direcciones)}", direcciones


def probar_tcp(host: str, port: int, timeout: float) -> tuple[str, str, str]:
    inicio = time.perf_counter()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        local = sock.getsockname()
        remoto = sock.getpeername()
    ms = (time.perf_counter() - inicio) * 1000
    return (
        OK,
        "conexion_exitosa",
        f"listener aceptó la conexión en {remoto[0]}:{remoto[1]} (origen {local[0]}) en {ms:.1f} ms",
    )


def estado_contenedor(nombre: str) -> tuple[str, str, str]:
    """Estado según Docker. Se lee el JSON completo de docker inspect y se
    interpreta en Python: las plantillas --format fallan en algunas versiones
    de Docker cuando el contenedor no define healthcheck."""
    out = subprocess.run(
        ["docker", "inspect", nombre],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    if out.returncode != 0:
        mensaje = (out.stderr or out.stdout).strip().splitlines()
        motivo = mensaje[-1] if mensaje else f"rc={out.returncode}"
        clase = "contenedor_inexistente" if "no such" in motivo.lower() else "error_docker"
        return FALLA, clase, f"docker inspect {nombre}: {motivo[:200]}"

    try:
        datos = json.loads(out.stdout)[0]
    except Exception as error:  # noqa: BLE001
        return SKIP, "herramienta_no_disponible", f"no se pudo interpretar docker inspect: {error}"

    estado = datos.get("State") or {}
    status = estado.get("Status", "desconocido")
    health = (estado.get("Health") or {}).get("Status") or "sin healthcheck"
    puertos = []
    for interno, publicados in ((datos.get("NetworkSettings") or {}).get("Ports") or {}).items():
        for pub in publicados or []:
            puertos.append(f"{interno}->{pub.get('HostIp', '')}:{pub.get('HostPort', '')}")
    detalle = (
        f"contenedor={nombre}; estado={status}; health={health}; iniciado={estado.get('StartedAt', '-')}; "
        f"puertos (interno->publicado)={', '.join(sorted(set(puertos))) or 'ninguno publicado'}"
    )
    if status != "running":
        return FALLA, "contenedor_detenido", detalle
    if health not in ("healthy", "sin healthcheck"):
        return ADVERTENCIA, f"contenedor_{health}", detalle
    return OK, "contenedor_en_ejecucion", detalle


def evaluar(
    cfg: Config,
    productos: list[str],
    redactar: Redactor,
    incluir_api: bool = True,
) -> list[Resultado]:
    resultados: list[Resultado] = []
    timeout = cfg.timeout

    # --- Proceso: estado del contenedor según Docker (informativo) ---
    if docker_disponible():
        activos = docker_contenedores()
        for clave in productos:
            spec = PRODUCTOS[clave]
            nombre = resolver_contenedor(cfg, clave, activos) or cfg.contenedor(clave)
            try:
                estado, clasif, detalle = estado_contenedor(nombre)
            except Exception as error:  # noqa: BLE001
                estado, clasif, detalle = SKIP, "herramienta_no_disponible", str(error)
            resultados.append(
                completar_diagnostico(
                    Resultado(
                        producto=spec["nombre"],
                        capa="proceso",
                        prueba="estado del contenedor (docker inspect)",
                        objetivo=nombre,
                        estado=estado,
                        clasificacion=clasif,
                        detalle=redactar(detalle),
                        cliente="docker CLI",
                        requerida=False,
                        pregunta="¿Docker informa el contenedor como iniciado y qué puertos publica?",
                        no_concluye=(
                            "Que el producto acepte conexiones, autentique o responda consultas: "
                            "un contenedor activo no equivale a una dependencia disponible."
                        ),
                    )
                )
            )
    else:
        for clave in productos:
            resultados.append(
                Resultado(
                    producto=PRODUCTOS[clave]["nombre"],
                    capa="proceso",
                    prueba="estado del contenedor (docker inspect)",
                    objetivo=cfg.contenedor(clave),
                    estado=SKIP,
                    clasificacion="herramienta_no_disponible",
                    detalle="Docker CLI no disponible desde este entorno.",
                    cliente="docker CLI",
                    requerida=False,
                    pregunta="¿Docker informa el contenedor como iniciado?",
                    no_concluye="Nada: la prueba no se ejecutó.",
                )
            )

    # --- Resolución + TCP ---
    for obj in objetivos(cfg, productos, incluir_api):
        destino = f"{obj['host']}:{obj['port']}"
        etiqueta = f"{obj['descripcion']} ({obj['protocolo']})"

        inicio = time.perf_counter()
        try:
            estado, clasif, detalle, _ = probar_resolucion(obj["host"], timeout)
        except Exception as error:  # noqa: BLE001
            estado, clasif, detalle = FALLA, clasificar_error_red(error), f"{type(error).__name__}: {error}"
            if clasif == "error_driver":
                clasif = "host_no_resuelto"
        dur = round((time.perf_counter() - inicio) * 1000, 2)

        res_resol = completar_diagnostico(
            Resultado(
                producto=obj["producto"],
                capa="resolucion",
                prueba=f"resolución de {obj['host']}",
                objetivo=obj["host"],
                estado=estado,
                clasificacion=clasif,
                detalle=redactar(detalle),
                duracion_ms=dur,
                cliente="socket.getaddrinfo",
                requerida=obj["requerido"],
                pregunta="¿El nombre configurado se convierte en una dirección IP desde este entorno?",
                no_concluye="Que haya un proceso escuchando en el puerto.",
            )
        )
        resultados.append(res_resol)

        if res_resol.estado == FALLA:
            resultados.append(
                Resultado(
                    producto=obj["producto"],
                    capa="tcp",
                    prueba=etiqueta,
                    objetivo=destino,
                    estado=BLOQUEADA,
                    clasificacion="bloqueada_por_capa_previa",
                    detalle="No se ejecutó: el host no se resolvió.",
                    cliente="socket TCP",
                    requerida=obj["requerido"],
                )
            )
            continue

        inicio = time.perf_counter()
        try:
            estado, clasif, detalle = probar_tcp(obj["host"], obj["port"], timeout)
        except Exception as error:  # noqa: BLE001
            estado, clasif, detalle = FALLA, clasificar_error_red(error), f"{type(error).__name__}: {error}"
        dur = round((time.perf_counter() - inicio) * 1000, 2)

        resultados.append(
            completar_diagnostico(
                Resultado(
                    producto=obj["producto"],
                    capa="tcp",
                    prueba=etiqueta,
                    objetivo=destino,
                    estado=estado,
                    clasificacion=clasif,
                    detalle=redactar(detalle) + (f" (timeout configurado {timeout:.1f} s)" if clasif == "timeout" else ""),
                    duracion_ms=dur,
                    cliente="socket TCP",
                    requerida=obj["requerido"],
                    pregunta="¿Existe un listener que acepte conexiones TCP en host:puerto desde este entorno?",
                    no_concluye=(
                        "Que el listener sea el producto correcto (puerto equivocado), que la identidad sea válida, "
                        "que exista el contexto o que una consulta funcione."
                    ),
                )
            )
        )

    return resultados


# --------------------------------------------------------------------------
# Demostración RNF3: la misma prueba desde dentro de un contenedor
# --------------------------------------------------------------------------

def desde_contenedor(cfg: Config, contenedor: str, productos: list[str], redactar: Redactor) -> list[Resultado]:
    resultados = []
    timeout = max(1, int(round(cfg.timeout)))
    origen = f"contenedor {contenedor} (red Docker)"

    if not docker_disponible():
        return [
            Resultado(
                producto="Entorno",
                capa="tcp",
                prueba="TCP desde contenedor",
                objetivo=contenedor,
                estado=SKIP,
                clasificacion="herramienta_no_disponible",
                detalle="Docker CLI no disponible.",
                origen=origen,
                requerida=False,
            )
        ]

    for obj in objetivos(cfg, productos, incluir_api=False):
        for host in ("127.0.0.1", "host.docker.internal"):
            script = (
                f"timeout {timeout} bash -c '</dev/tcp/{host}/{obj['port']}' 2>&1; echo \"rc=$?\""
            )
            inicio = time.perf_counter()
            try:
                out = subprocess.run(
                    ["docker", "exec", contenedor, "bash", "-c", script],
                    capture_output=True,
                    text=True,
                    timeout=timeout + 10,
                )
                salida = (out.stdout + out.stderr).strip()
            except Exception as error:  # noqa: BLE001
                salida = f"error: {error}"
            dur = round((time.perf_counter() - inicio) * 1000, 2)

            rc = salida.rsplit("rc=", 1)[-1].strip() if "rc=" in salida else "?"
            texto = salida.lower()
            if rc == "0":
                estado, clasif = OK, "conexion_exitosa"
            elif "executable file not found" in texto or "no such container" in texto or "is not running" in texto:
                estado, clasif = SKIP, "herramienta_no_disponible"
            elif rc == "124":
                estado, clasif = FALLA, "timeout"
            elif "refused" in texto:
                estado, clasif = FALLA, "connection_refused"
            elif "not known" in texto or "resolve" in texto or "no address" in texto:
                estado, clasif = FALLA, "host_no_resuelto"
            else:
                estado, clasif = FALLA, "error_driver"

            interpretacion = (
                "127.0.0.1 dentro del contenedor es el propio contenedor, no la notebook"
                if host == "127.0.0.1" else
                "host.docker.internal apunta a la notebook (Docker Desktop) y alcanza los puertos publicados"
            )
            resultados.append(
                completar_diagnostico(
                    Resultado(
                        producto=obj["producto"],
                        capa="tcp",
                        prueba=f"{obj['descripcion']} desde contenedor via {host}",
                        objetivo=f"{host}:{obj['port']}",
                        estado=estado,
                        clasificacion=clasif,
                        detalle=redactar(f"{salida[-200:]} | {interpretacion}"),
                        duracion_ms=dur,
                        origen=origen,
                        cliente="bash /dev/tcp (docker exec)",
                        requerida=False,
                        pregunta="¿El mismo host:puerto es alcanzable desde otro origen (un contenedor)?",
                        no_concluye="Nada sobre la conexión de la API, que corre en la notebook.",
                    )
                )
            )
    return resultados


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(description="Hito 11 - resolución y TCP")
    parser.add_argument("--producto", default="todos", choices=["todos", *PRODUCTOS])
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR")
    parser.add_argument("--etiqueta", default="")
    parser.add_argument("--sin-api", action="store_true", help="no probar el puerto de la API")
    parser.add_argument("--desde-contenedor", default="", metavar="CONTENEDOR",
                        help="repetir la prueba TCP desde dentro de un contenedor (RNF3)")
    args = parser.parse_args(argv)

    cfg = Config(parse_overrides(args.set))
    redactar = Redactor(cfg.secretos())
    productos = list(PRODUCTOS) if args.producto == "todos" else [args.producto]

    contexto = contexto_ejecucion(cfg, "tcp")
    print("=== HITO 11 - PROCESO, RESOLUCION Y TCP ===")
    print(f"Fecha: {contexto['fecha']} | Origen: {contexto['origen_de_las_pruebas']} | Timeout: {cfg.timeout} s")
    print()

    resultados = evaluar(cfg, productos, redactar, incluir_api=not args.sin_api)
    if args.desde_contenedor:
        resultados += desde_contenedor(cfg, args.desde_contenedor, productos, redactar)

    for r in resultados:
        imprimir_resultado(r)
    imprimir_resumen(resultados)

    txt, _ = escribir_evidencia("resultados_tcp", contexto, resultados, redactar, args.etiqueta)
    print(f"\nEvidencia: {txt}")
    return 1 if any(r.estado == FALLA and r.requerida for r in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())
