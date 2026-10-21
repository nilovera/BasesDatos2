"""Capas 5 a 9: protocolo, autenticación, autorización, contexto y operación.

RF6 a RF14, RNF4 a RNF6, RNF14. Cada producto se evalúa con su driver
nativo (los mismos paquetes y versiones que usa la API), desde el mismo
entorno que la API, avanzando de menor a mayor costo. Una capa requerida
fallida bloquea las siguientes.

Además de las pruebas positivas se ejecutan pruebas negativas controladas
(recurso inexistente, contexto inexistente, consulta inválida) para que el
diagnóstico distinga "ausencia válida" de "error de conexión".

Todas las operaciones son de lectura, ping o retorno constante. La única
escritura es opcional y ajena al dominio: una clave ``diag:hito11:*`` en
Redis con TTL de 2 segundos para demostrar la expiración (se desactiva con
``--sin-escritura``).

Opcional ``--cli``: ejecuta además el cliente de línea de comandos de cada
producto dentro de su contenedor (mongosh, cypher-shell, cqlsh, redis-cli,
influxdb3, iris). Ese origen es distinto al de la API y se informa como tal.
"""

from __future__ import annotations

import argparse
import socket
import struct
import subprocess
import sys
import time
import uuid

from common import (
    ADVERTENCIA,
    FALLA,
    NO_APLICA,
    OK,
    PRODUCTOS,
    SKIP,
    Cadena,
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
    version_paquete,
)


NEGATIVA = "prueba negativa controlada"


# ==========================================================================
# MongoDB
# ==========================================================================

def evaluar_mongodb(cfg: Config, redactar: Redactor) -> list[Resultado]:
    host = cfg.get("MONGODB_HOST", "127.0.0.1")
    port = cfg.get_int("MONGODB_PORT", 27017)
    database = cfg.get("MONGODB_DATABASE", "fixture2030")
    auth_source = cfg.get("MONGODB_AUTH_SOURCE", "admin")
    equipo = cfg.get("MONGO_EQUIPO_DEMO", "EQ-01")
    timeout_ms = int(cfg.timeout * 1000)
    cliente = f"pymongo {version_paquete('pymongo')}"
    objetivo = f"{host}:{port}/{database}"

    try:
        from pymongo import MongoClient
        from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
    except ImportError as error:
        cadena = Cadena("MongoDB", clasificar_error_red, redactar, "pymongo", objetivo)
        cadena.omitir_todo(f"pymongo no instalado: {error}", "herramienta_no_disponible",
                           [("protocolo", "hello"), ("operacion", "lectura")])
        return cadena.resultados

    def clasificar(error: BaseException) -> str:
        if isinstance(error, OperationFailure):
            if error.code == 18:
                return "auth_fallida"
            if error.code == 13:
                return "sin_permiso"
            return "error_driver"
        texto = str(error).lower()
        if isinstance(error, ServerSelectionTimeoutError):
            red = clasificar_error_red(error)
            if red != "error_driver":
                return red
            if "connection closed" in texto or "unexpected" in texto or "invalid message" in texto:
                return "protocolo_inesperado"
            return "timeout"
        return clasificar_error_red(error)

    comunes = dict(
        host=host,
        port=port,
        directConnection=True,
        serverSelectionTimeoutMS=timeout_ms,
        connectTimeoutMS=timeout_ms,
        socketTimeoutMS=timeout_ms,
    )

    anon = MongoClient(**comunes)
    auth = MongoClient(
        **comunes,
        username=cfg.get("MONGODB_USERNAME"),
        password=cfg.get("MONGODB_PASSWORD"),
        authSource=auth_source,
    )
    cadena = Cadena("MongoDB", clasificar, redactar, cliente, objetivo)

    try:
        def protocolo():
            hello = anon.admin.command("hello")
            version = ""
            try:
                version = anon.admin.command("buildInfo").get("version", "")
            except Exception:
                version = "no informada sin autenticación"
            return (
                OK,
                "handshake_ok",
                f"hello respondió: isWritablePrimary={hello.get('isWritablePrimary')}, "
                f"maxWireVersion={hello.get('maxWireVersion')}, version servidor={version}",
            )

        cadena.paso(
            "protocolo", "comando hello sin credenciales", protocolo,
            "¿El listener habla MongoDB Wire Protocol?",
            "Que la identidad configurada sea válida.",
        )

        def autenticacion():
            status = auth[auth_source].command("connectionStatus")
            info = status.get("authInfo", {})
            usuarios = info.get("authenticatedUsers", [])
            roles = sorted({r.get("role", "?") for r in info.get("authenticatedUserRoles", [])})
            if not usuarios:
                return FALLA, "auth_fallida", "connectionStatus no informa usuarios autenticados"
            return (
                OK,
                "autenticado",
                f"{len(usuarios)} identidad autenticada contra authSource={auth_source}; roles={', '.join(roles) or '-'} "
                "(nombre de usuario omitido)",
            )

        cadena.paso(
            "autenticacion", "connectionStatus con credenciales", autenticacion,
            "¿El servidor acepta usuario/password contra la base de autenticación configurada?",
            "Que el usuario tenga permisos sobre la database del Fixture ni que la database exista.",
        )

        def autorizacion():
            nombres = auth[database].list_collection_names(maxTimeMS=timeout_ms)
            return OK, "autorizado", f"listCollections permitido sobre '{database}' ({len(nombres)} colecciones)"

        cadena.paso(
            "autorizacion", f"listCollections sobre {database}", autorizacion,
            "¿La identidad tiene permiso para operar sobre la database del Fixture?",
            "Que la database contenga los datos esperados (MongoDB no falla ante una database inexistente).",
        )

        def contexto():
            dbs = auth.list_database_names()
            nombres = set(auth[database].list_collection_names(maxTimeMS=timeout_ms))
            esperadas = {"equipos", "jugadores"}
            faltan = esperadas - nombres
            if database not in dbs:
                return FALLA, "contexto_inexistente", (
                    f"la database '{database}' no existe en el servidor (MongoDB la crearía vacía al escribir)"
                )
            if faltan:
                return FALLA, "tabla_inexistente", f"faltan colecciones: {', '.join(sorted(faltan))}"
            return OK, "contexto_ok", f"database '{database}' existe con colecciones equipos y jugadores"

        cadena.paso(
            "contexto", "database y colecciones del módulo", contexto,
            "¿La database configurada existe y contiene las colecciones del módulo documental?",
            "Que una consulta concreta devuelva datos.",
        )

        def operacion():
            doc = auth[database]["equipos"].find_one(
                {"_id": equipo},
                {"_id": 1, "nombre": 1, "confederacion": 1, "ranking": 1},
                max_time_ms=timeout_ms,
            )
            equipos = auth[database]["equipos"].estimated_document_count(maxTimeMS=timeout_ms)
            jugadores = auth[database]["jugadores"].estimated_document_count(maxTimeMS=timeout_ms)
            if doc is None:
                return ADVERTENCIA, "recurso_inexistente", (
                    f"conexión correcta pero el equipo de demostración {equipo} no existe "
                    f"(equipos={equipos}, jugadores={jugadores})"
                )
            return OK, "lectura_ok", (
                f"find_one({{_id:'{equipo}'}}) devolvió campos {sorted(doc)}; "
                f"conteo estimado equipos={equipos}, jugadores={jugadores}"
            )

        cadena.paso(
            "operacion", f"find_one equipos {{_id:{equipo}}} con proyección", operacion,
            "¿El cliente puede leer un documento del módulo equipos/jugadores con límite de tiempo?",
            "Rendimiento con volumen o concurrencia (Hito 12).",
        )

        def inexistente():
            doc = auth[database]["equipos"].find_one({"_id": "EQ-99"}, max_time_ms=timeout_ms)
            if doc is None:
                return OK, "recurso_inexistente", "EQ-99 devolvió None: ausencia válida, no es un error de conexión"
            return ADVERTENCIA, "respuesta_inesperada", "EQ-99 existe; elegir otro identificador inexistente"

        cadena.paso(
            "operacion", f"{NEGATIVA}: documento inexistente EQ-99", inexistente,
            "¿Un documento inexistente se distingue de una falla?",
            "-", requerida=False,
        )

        def db_inexistente():
            nombre = "fixture2030_diag_inexistente"
            colecciones = auth[nombre].list_collection_names(maxTimeMS=timeout_ms)
            return OK, "contexto_inexistente_silencioso", (
                f"database '{nombre}': list_collection_names devolvió {len(colecciones)} colecciones sin error. "
                "MongoDB no falla ante una database o colección inexistente; por eso la API valida el contexto en /health/dependencias."
            )

        cadena.paso(
            "contexto", f"{NEGATIVA}: database inexistente", db_inexistente,
            "¿Cómo responde MongoDB si el contexto configurado está mal escrito?",
            "-", requerida=False,
        )
    finally:
        anon.close()
        auth.close()

    return cadena.resultados


# ==========================================================================
# Neo4j
# ==========================================================================

def bolt_handshake(host: str, port: int, timeout: float) -> tuple[str, str, str]:
    """Handshake Bolt real, sin credenciales (magic + 4 versiones)."""
    propuestas = [
        bytes([0, 0, 0, 6]),   # 6.0
        bytes([0, 8, 8, 5]),   # 5.8 .. 5.0
        bytes([0, 0, 4, 4]),   # 4.4
        bytes([0, 0, 3, 4]),   # 4.3
    ]
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(b"\x60\x60\xb0\x17" + b"".join(propuestas))
        data = b""
        while len(data) < 4:
            chunk = sock.recv(4 - len(data))
            if not chunk:
                break
            data += chunk
    if len(data) < 4:
        return FALLA, "protocolo_inesperado", f"respuesta incompleta al handshake Bolt ({data!r})"
    if data.startswith(b"HTTP"):
        return FALLA, "protocolo_inesperado", "el puerto respondió HTTP: es el Browser (7474), no Bolt (7687)"
    _, _, minor, major = struct.unpack("4B", data)
    if major == 0 and minor == 0:
        return FALLA, "protocolo_inesperado", "el servidor rechazó todas las versiones Bolt propuestas"
    return OK, "handshake_ok", f"handshake Bolt aceptado; versión negociada {major}.{minor}"


def evaluar_neo4j(cfg: Config, redactar: Redactor) -> list[Resultado]:
    uri = cfg.get("NEO4J_URI", "bolt://127.0.0.1:7687")
    database = cfg.get("NEO4J_DATABASE", "neo4j")
    http_url = cfg.get("NEO4J_HTTP_URL", "http://127.0.0.1:7474")
    partido = cfg.get("NEO4J_PARTIDO_DEMO", "PAR-0001")
    host, port = host_port_from_url(uri, 7687)
    timeout = cfg.timeout
    cliente = f"neo4j-python-driver {version_paquete('neo4j')}"
    objetivo = f"{host}:{port}/{database}"

    try:
        import httpx
        from neo4j import GraphDatabase, Query
        from neo4j.exceptions import AuthError, ClientError, Forbidden, ServiceUnavailable
    except ImportError as error:
        cadena = Cadena("Neo4j", clasificar_error_red, redactar, "neo4j", objetivo)
        cadena.omitir_todo(f"driver no instalado: {error}", "herramienta_no_disponible",
                           [("protocolo", "Bolt"), ("operacion", "Cypher")])
        return cadena.resultados

    def clasificar(error: BaseException) -> str:
        code = getattr(error, "code", "") or ""
        if isinstance(error, AuthError) or "Unauthorized" in code:
            return "auth_fallida"
        if isinstance(error, Forbidden) or "Forbidden" in code:
            return "sin_permiso"
        if "DatabaseNotFound" in code:
            return "contexto_inexistente"
        if "SyntaxError" in code:
            return "consulta_invalida"
        if isinstance(error, ServiceUnavailable):
            red = clasificar_error_red(error)
            return red if red != "error_driver" else "connection_refused"
        if isinstance(error, ClientError):
            return "error_driver"
        return clasificar_error_red(error)

    cadena = Cadena("Neo4j", clasificar, redactar, cliente, objetivo)

    def portal_http():
        r = httpx.get(http_url, timeout=timeout, headers={"Accept": "application/json"})
        info = {}
        try:
            info = r.json()
        except Exception:
            pass
        version = info.get("neo4j_version", "no informada")
        bolt = info.get("bolt_direct") or info.get("bolt_routing") or "-"
        return OK, "portal_http_ok", f"HTTP {r.status_code}; neo4j_version={version}; bolt anunciado={bolt}"

    cadena.paso(
        "protocolo", "portal HTTP / Browser", portal_http,
        "¿Responde el portal HTTP que usa una persona desde el navegador?",
        "Nada sobre Bolt: la API no usa HTTP. Un portal accesible no implica Bolt accesible.",
        requerida=False, objetivo=http_url, cliente="httpx", necesita_cadena=False,
    )

    cadena.paso(
        "protocolo", "handshake Bolt (sin credenciales)", lambda: bolt_handshake(host, port, timeout),
        "¿El puerto configurado habla Bolt y negocia una versión compatible?",
        "Que la identidad configurada sea válida.",
        cliente="socket (handshake Bolt manual)",
    )

    driver = GraphDatabase.driver(
        uri,
        auth=(cfg.get("NEO4J_USERNAME", ""), cfg.get("NEO4J_PASSWORD", "")),
        connection_timeout=timeout,
        max_transaction_retry_time=0,
    )

    try:
        def autenticacion():
            ok = driver.verify_authentication()
            if not ok:
                return FALLA, "auth_fallida", "verify_authentication devolvió False"
            info = driver.get_server_info()
            return OK, "autenticado", f"credenciales aceptadas; agent={info.agent}; protocolo Bolt={info.protocol_version}"

        cadena.paso(
            "autenticacion", "verify_authentication", autenticacion,
            "¿El servidor acepta la identidad configurada por Bolt?",
            "Que la database seleccionada exista ni que la identidad pueda leerla.",
        )

        def contexto():
            with driver.session(database=database) as session:
                session.run(Query("RETURN 1 AS ok", timeout=timeout)).consume()
            return OK, "contexto_ok", f"database '{database}' seleccionada y operativa (RETURN 1)"

        cadena.paso(
            "contexto", f"selección de database {database}", contexto,
            "¿La database configurada existe y acepta transacciones?",
            "Que contenga el grafo del Fixture.",
        )

        def autorizacion():
            with driver.session(database=database, default_access_mode="READ") as session:
                record = session.run(
                    Query("MATCH (e:Equipo) RETURN count(e) AS total", timeout=timeout)
                ).single()
            return OK, "autorizado", f"lectura permitida; nodos :Equipo={record['total']}"

        cadena.paso(
            "autorizacion", "lectura en modo READ sobre :Equipo", autorizacion,
            "¿La identidad puede leer nodos del dominio en esa database?",
            "Que exista el partido de demostración.",
        )

        consulta = (
            "MATCH (p:Partido {codigo: $codigo}) "
            "OPTIONAL MATCH (p)-[:DISPUTA]->(e:Equipo) "
            "OPTIONAL MATCH (ev:Evento)-[:OCURRE_EN]->(p) "
            "RETURN p.codigo AS codigo, count(DISTINCT e) AS equipos, count(DISTINCT ev) AS eventos LIMIT 1"
        )

        def operacion():
            with driver.session(database=database, default_access_mode="READ") as session:
                record = session.run(Query(consulta, timeout=timeout), codigo=partido).single()
            if record is None:
                return ADVERTENCIA, "recurso_inexistente", f"conexión correcta pero el partido {partido} no existe"
            return OK, "lectura_ok", (
                f"Cypher parametrizado ($codigo={partido}): equipos={record['equipos']}, eventos={record['eventos']}"
            )

        cadena.paso(
            "operacion", f"Cypher parametrizado partido {partido}", operacion,
            "¿Se puede ejecutar la lectura acotada que usa el módulo de partidos/eventos?",
            "Rendimiento con volumen (Hito 12).",
        )

        def inexistente():
            with driver.session(database=database, default_access_mode="READ") as session:
                record = session.run(Query(consulta, timeout=timeout), codigo="PAR-9999").single()
            if record is None:
                return OK, "recurso_inexistente", "PAR-9999: resultado vacío sin error (ausencia válida ≠ error de conexión)"
            return ADVERTENCIA, "respuesta_inesperada", "PAR-9999 existe en el grafo"

        cadena.paso(
            "operacion", f"{NEGATIVA}: partido inexistente PAR-9999", inexistente,
            "¿Un partido inexistente se distingue de un error de conexión?",
            "-", requerida=False,
        )

        def db_inexistente():
            try:
                with driver.session(database="fixture2030diaginexistente") as session:
                    session.run(Query("RETURN 1", timeout=timeout)).consume()
            except Exception as error:  # noqa: BLE001
                clase = clasificar(error)
                if clase == "contexto_inexistente":
                    return OK, "contexto_inexistente", f"error esperado: {getattr(error, 'code', type(error).__name__)}"
                return ADVERTENCIA, clase, f"error distinto al esperado: {type(error).__name__}"
            return ADVERTENCIA, "respuesta_inesperada", "la database inexistente aceptó la transacción"

        cadena.paso(
            "contexto", f"{NEGATIVA}: database inexistente", db_inexistente,
            "¿Una database mal configurada produce un error identificable?",
            "-", requerida=False,
        )
    finally:
        driver.close()

    return cadena.resultados


# ==========================================================================
# Cassandra
# ==========================================================================

def evaluar_cassandra(cfg: Config, redactar: Redactor) -> list[Resultado]:
    hosts = [h.strip() for h in (cfg.get("CASSANDRA_HOSTS", "127.0.0.1") or "").split(",") if h.strip()]
    port = cfg.get_int("CASSANDRA_PORT", 9042)
    keyspace = cfg.get("CASSANDRA_KEYSPACE", "fixture2030_comentarios")
    tabla = cfg.get("CASSANDRA_TABLA", "comentarios_por_partido")
    partido = cfg.get("CASSANDRA_PARTIDO_DEMO", "PAR-0001")
    bucket = cfg.get("CASSANDRA_BUCKET_DEMO", "203006131800")
    timeout = cfg.timeout
    cliente = f"cassandra-driver {version_paquete('cassandra-driver')}"
    objetivo = f"{','.join(hosts)}:{port}/{keyspace}"

    try:
        from cassandra import (
            AuthenticationFailed,
            InvalidRequest,
            OperationTimedOut,
            ReadTimeout,
            Unauthorized,
        )
        from cassandra.cluster import Cluster, NoHostAvailable
        from cassandra.protocol import SyntaxException
    except ImportError as error:
        cadena = Cadena("Cassandra", clasificar_error_red, redactar, "cassandra-driver", objetivo)
        cadena.omitir_todo(f"driver no instalado: {error}", "herramienta_no_disponible",
                           [("protocolo", "CQL"), ("operacion", "SELECT")])
        return cadena.resultados

    def clasificar(error: BaseException) -> str:
        if isinstance(error, NoHostAvailable):
            causas = list(getattr(error, "errors", {}).values())
            for causa in causas:
                if isinstance(causa, AuthenticationFailed):
                    return "auth_fallida"
                if isinstance(causa, OperationTimedOut):
                    return "timeout"
                red = clasificar_error_red(causa)
                if red != "error_driver":
                    return red
            return "connection_refused" if not causas else "error_driver"
        if isinstance(error, AuthenticationFailed):
            return "auth_fallida"
        if isinstance(error, Unauthorized):
            return "sin_permiso"
        if isinstance(error, (OperationTimedOut, ReadTimeout)):
            return "timeout"
        if isinstance(error, SyntaxException):
            return "consulta_invalida"
        if isinstance(error, InvalidRequest):
            texto = str(error).lower()
            if "keyspace" in texto:
                return "contexto_inexistente"
            if "unconfigured table" in texto or "table" in texto:
                return "tabla_inexistente"
            return "consulta_invalida"
        return clasificar_error_red(error)

    cadena = Cadena("Cassandra", clasificar, redactar, cliente, objetivo)

    kwargs = dict(
        contact_points=hosts,
        port=port,
        connect_timeout=timeout,
        control_connection_timeout=timeout,
    )
    if cfg.definida("CASSANDRA_USERNAME"):
        from cassandra.auth import PlainTextAuthProvider

        kwargs["auth_provider"] = PlainTextAuthProvider(
            username=cfg.get("CASSANDRA_USERNAME"),
            password=cfg.get("CASSANDRA_PASSWORD", ""),
        )

    cluster = Cluster(**kwargs)
    estado = {}

    try:
        def protocolo():
            session = cluster.connect()
            session.default_timeout = timeout
            estado["session"] = session
            row = session.execute(
                "SELECT release_version, cluster_name, data_center FROM system.local", timeout=timeout
            ).one()
            return OK, "handshake_ok", (
                f"sesión CQL establecida; protocolo nativo v{cluster.protocol_version}; "
                f"Cassandra {row.release_version}; cluster={row.cluster_name}; dc={row.data_center}"
            )

        cadena.paso(
            "protocolo", "sesión CQL sin keyspace (system.local)", protocolo,
            "¿El puerto habla el protocolo nativo CQL y se puede abrir una sesión?",
            "Que el keyspace del módulo exista.",
        )

        def autenticacion():
            if "auth_provider" in kwargs:
                return OK, "autenticado", "sesión abierta con PlainTextAuthProvider (credenciales ocultas)"
            return NO_APLICA, "sin_autenticacion_configurada", (
                "el cluster aceptó la sesión sin credenciales: en este laboratorio no exige autenticación "
                "(AllowAllAuthenticator). En producción esta capa debería existir."
            )

        cadena.paso(
            "autenticacion", "mecanismo de autenticación", autenticacion,
            "¿El cluster exige identidad y la configurada es aceptada?",
            "Permisos sobre el keyspace.",
        )

        def contexto():
            session = estado["session"]
            ks = session.execute(
                "SELECT keyspace_name, replication FROM system_schema.keyspaces WHERE keyspace_name = %s",
                [keyspace], timeout=timeout,
            ).one()
            if ks is None:
                return FALLA, "contexto_inexistente", f"keyspace '{keyspace}' no existe"
            session.set_keyspace(keyspace)
            return OK, "contexto_ok", f"keyspace '{keyspace}' seleccionado; replicación={dict(ks.replication)}"

        cadena.paso(
            "contexto", f"keyspace {keyspace}", contexto,
            "¿El keyspace configurado existe y puede seleccionarse?",
            "Que la tabla y su clave de partición sean las esperadas.",
        )

        def tabla_particion():
            session = estado["session"]
            filas = list(session.execute(
                "SELECT column_name, kind, position, clustering_order FROM system_schema.columns "
                "WHERE keyspace_name = %s AND table_name = %s",
                [keyspace, tabla], timeout=timeout,
            ))
            if not filas:
                return FALLA, "tabla_inexistente", f"la tabla '{tabla}' no existe en '{keyspace}'"
            pk = [f.column_name for f in sorted(filas, key=lambda f: f.position) if f.kind == "partition_key"]
            ck = [
                f"{f.column_name} {f.clustering_order.upper()}"
                for f in sorted(filas, key=lambda f: f.position) if f.kind == "clustering"
            ]
            return OK, "contexto_ok", f"tabla {tabla}: PRIMARY KEY (({', '.join(pk)}), {', '.join(ck)})"

        cadena.paso(
            "contexto", f"tabla {tabla} y patrón de partición", tabla_particion,
            "¿Existe la tabla del módulo y qué clave de partición exige la consulta?",
            "Que la partición de demostración tenga datos.",
        )

        def autorizacion():
            session = estado["session"]
            session.execute(f"SELECT partido_id FROM {tabla} LIMIT 1", timeout=timeout)
            return OK, "autorizado", f"SELECT permitido sobre {keyspace}.{tabla}"

        cadena.paso(
            "autorizacion", f"SELECT LIMIT 1 sobre {tabla}", autorizacion,
            "¿La sesión puede leer la tabla del módulo?",
            "Que una partición concreta tenga filas.",
        )

        def operacion():
            session = estado["session"]
            filas = list(session.execute(
                f"SELECT comentario_id, creado_en FROM {tabla} WHERE partido_id = %s AND bucket_10min = %s LIMIT 3",
                [partido, bucket], timeout=timeout,
            ))
            if not filas:
                return ADVERTENCIA, "vacio_valido", f"partición ({partido}, {bucket}) sin filas"
            return OK, "lectura_ok", f"partición (partido_id={partido}, bucket_10min={bucket}): {len(filas)} filas (LIMIT 3)"

        cadena.paso(
            "operacion", f"lectura limitada partición ({partido}, {bucket})", operacion,
            "¿Se puede leer una partición del módulo de comentarios con LIMIT?",
            "Rendimiento con volumen (Hito 12).",
        )

        def vacia():
            session = estado["session"]
            filas = list(session.execute(
                f"SELECT comentario_id FROM {tabla} WHERE partido_id = %s AND bucket_10min = %s LIMIT 3",
                ["PAR-9999", bucket], timeout=timeout,
            ))
            return OK, "vacio_valido", f"partición inexistente PAR-9999: {len(filas)} filas, sin error (lista vacía ≠ timeout)"

        cadena.paso(
            "operacion", f"{NEGATIVA}: partición vacía", vacia,
            "¿Una partición sin datos se distingue de un timeout?",
            "-", requerida=False,
        )

        def keyspace_inexistente():
            session = estado["session"]
            try:
                session.execute("SELECT * FROM ks_diag_inexistente.tabla LIMIT 1", timeout=timeout)
            except Exception as error:  # noqa: BLE001
                clase = clasificar(error)
                ok = clase in ("contexto_inexistente", "tabla_inexistente")
                return (OK if ok else ADVERTENCIA), clase, f"error esperado: {type(error).__name__}"
            return ADVERTENCIA, "respuesta_inesperada", "la consulta no falló"

        cadena.paso(
            "contexto", f"{NEGATIVA}: keyspace inexistente", keyspace_inexistente,
            "¿Un keyspace mal configurado produce un error identificable?",
            "-", requerida=False,
        )

        def tabla_inexistente():
            session = estado["session"]
            try:
                session.execute("SELECT * FROM tabla_diag_inexistente LIMIT 1", timeout=timeout)
            except Exception as error:  # noqa: BLE001
                clase = clasificar(error)
                return (OK if clase == "tabla_inexistente" else ADVERTENCIA), clase, f"error esperado: {type(error).__name__}"
            return ADVERTENCIA, "respuesta_inesperada", "la consulta no falló"

        cadena.paso(
            "contexto", f"{NEGATIVA}: tabla inexistente", tabla_inexistente,
            "¿Una tabla inexistente se distingue de un problema de red?",
            "-", requerida=False,
        )

        def consulta_invalida():
            session = estado["session"]
            inicio = time.perf_counter()
            try:
                session.execute("SELEC partido_id FROM comentarios_por_partido", timeout=timeout)
            except Exception as error:  # noqa: BLE001
                ms = (time.perf_counter() - inicio) * 1000
                clase = clasificar(error)
                return (OK if clase == "consulta_invalida" else ADVERTENCIA), clase, (
                    f"{type(error).__name__} en {ms:.1f} ms: rechazo inmediato del servidor, no un timeout de conexión"
                )
            return ADVERTENCIA, "respuesta_inesperada", "la consulta inválida no falló"

        cadena.paso(
            "operacion", f"{NEGATIVA}: consulta CQL inválida", consulta_invalida,
            "¿Se distingue una consulta inválida de un timeout de conexión?",
            "-", requerida=False,
        )
    finally:
        try:
            cluster.shutdown()
        except Exception:
            pass

    return cadena.resultados


# ==========================================================================
# Redis
# ==========================================================================

def resp_ping(host: str, port: int, timeout: float, password: str | None) -> tuple[str, str, str]:
    """PING en RESP crudo para validar el protocolo independientemente del driver."""
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(b"*1\r\n$4\r\nPING\r\n")
        data = sock.recv(128)
    texto = data.decode("utf-8", errors="replace").strip()
    if texto.startswith("+PONG"):
        return OK, "handshake_ok", "RESP: PING -> +PONG sin credenciales"
    if texto.startswith("-NOAUTH"):
        return OK, "handshake_ok_requiere_auth", "RESP válido; el servidor exige AUTH (-NOAUTH)"
    if texto.startswith(("-", "+", ":", "$", "*")):
        return OK, "handshake_ok", f"RESP válido: {texto[:60]}"
    return FALLA, "protocolo_inesperado", f"la respuesta no es RESP: {texto[:60]!r} (¿puerto de otro servicio?)"


def evaluar_redis(cfg: Config, redactar: Redactor, permitir_escritura: bool) -> list[Resultado]:
    host = cfg.get("REDIS_HOST", "127.0.0.1")
    port = cfg.get_int("REDIS_PORT", 6379)
    db = cfg.get_int("REDIS_DATABASE", 0)
    password = cfg.get("REDIS_PASSWORD")
    sesion = cfg.get("REDIS_SESION_DEMO", "SES-API-0001")
    timeout = cfg.timeout
    cliente = f"redis-py {version_paquete('redis')}"
    objetivo = f"{host}:{port}/db{db}"

    try:
        import redis as redis_lib
        from redis.backoff import NoBackoff
        from redis.exceptions import AuthenticationError, ResponseError
        from redis.retry import Retry
    except ImportError as error:
        cadena = Cadena("Redis", clasificar_error_red, redactar, "redis-py", objetivo)
        cadena.omitir_todo(f"redis-py no instalado: {error}", "herramienta_no_disponible",
                           [("protocolo", "PING"), ("operacion", "GET")])
        return cadena.resultados

    def clasificar(error: BaseException) -> str:
        if isinstance(error, AuthenticationError):
            return "auth_fallida"
        if isinstance(error, ResponseError) and "NOAUTH" in str(error).upper():
            return "auth_requerida_sin_credencial"
        if isinstance(error, ResponseError) and "NOPERM" in str(error).upper():
            return "sin_permiso"
        return clasificar_error_red(error)

    cadena = Cadena("Redis", clasificar, redactar, cliente, objetivo)
    client = redis_lib.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True,
        retry=Retry(NoBackoff(), 0),
        socket_connect_timeout=timeout,
        socket_timeout=timeout,
    )
    estado = {}

    try:
        def protocolo():
            resultado = resp_ping(host, port, timeout, password)
            estado["requiere_auth"] = resultado[1] == "handshake_ok_requiere_auth"
            return resultado

        cadena.paso(
            "protocolo", "PING en RESP crudo", protocolo,
            "¿El puerto habla RESP (protocolo de Redis)?",
            "Que la base lógica tenga datos ni que la credencial sea válida.",
            cliente="socket (RESP manual)",
        )

        def autenticacion():
            if password:
                client.ping()
                return OK, "autenticado", "PING con la password configurada respondió PONG (valor oculto)"
            if estado.get("requiere_auth"):
                return FALLA, "auth_requerida_sin_credencial", "el servidor exige AUTH y no hay REDIS_PASSWORD"
            return NO_APLICA, "sin_autenticacion_configurada", (
                "el servidor respondió PONG sin AUTH: requirepass vacío en el laboratorio"
            )

        cadena.paso(
            "autenticacion", "AUTH / requirepass", autenticacion,
            "¿Redis exige identidad y la configurada es aceptada?",
            "Permisos ACL sobre comandos concretos.",
        )

        def contexto():
            client.ping()
            total = client.dbsize()
            info = client.info("server")
            return OK, "contexto_ok", (
                f"SELECT {db} implícito; claves en db{db}={total}; redis_version={info.get('redis_version')}"
            )

        cadena.paso(
            "contexto", f"base lógica db{db}", contexto,
            "¿La base lógica configurada es accesible y cuántas claves contiene?",
            "Que exista la clave de sesión de demostración.",
        )

        def operacion():
            clave = f"sesion:{sesion}"
            existe = client.exists(clave)
            ttl = client.ttl(clave)
            if ttl == -2:
                return OK, "clave_ausente", (
                    f"{clave}: EXISTS=0, TTL=-2 -> clave ausente o ya expirada. Redis respondió: "
                    "NO es Redis caído. (Para un 200 en la API ejecutar scripts/preparar_sesiones_redis.ps1)"
                )
            if ttl == -1:
                return ADVERTENCIA, "sin_expiracion", f"{clave}: existe pero sin TTL (una sesión debería expirar)"
            return OK, "clave_vigente", f"{clave}: EXISTS={existe}, TTL={ttl} s"

        cadena.paso(
            "operacion", f"EXISTS + TTL sesion:{sesion}", operacion,
            "¿Se puede leer la clave de sesión que usa el módulo y su expiración?",
            "Rendimiento o comportamiento bajo concurrencia (Hito 12).",
        )

        def expiracion():
            if not permitir_escritura:
                return SKIP, "escritura_deshabilitada", "omitida por --sin-escritura"
            clave = f"diag:hito11:{uuid.uuid4().hex[:8]}"
            client.set(clave, "diagnostico", ex=2)
            ttl_inicial = client.ttl(clave)
            time.sleep(2.5)
            existe = client.exists(clave)
            ttl_final = client.ttl(clave)
            if existe == 0 and ttl_final == -2:
                return OK, "clave_expirada", (
                    f"{clave} creada con EX 2 (TTL inicial {ttl_inicial}); a los 2.5 s EXISTS=0, TTL=-2. "
                    "Clave expirada y clave ausente se ven igual en Redis; ambas difieren de Redis no disponible "
                    "(ConnectionError en la capa TCP/protocolo)."
                )
            client.delete(clave)
            return ADVERTENCIA, "respuesta_inesperada", f"la clave seguía presente (TTL={ttl_final}); se eliminó"

        cadena.paso(
            "operacion", f"{NEGATIVA}: expiración de clave diag:hito11:* (TTL 2 s)", expiracion,
            "¿Cómo se ve una clave expirada frente a una ausente y frente a Redis caído?",
            "-", requerida=False,
        )
    finally:
        client.close()

    return cadena.resultados


# ==========================================================================
# InfluxDB 3
# ==========================================================================

def evaluar_influxdb(cfg: Config, redactar: Redactor) -> list[Resultado]:
    url = (cfg.get("INFLUXDB_URL", "http://127.0.0.1:8181") or "").rstrip("/")
    token = cfg.get("INFLUXDB_TOKEN", "")
    db_detalle = cfg.get("INFLUXDB_DETAIL_DATABASE", "fixture2030_detalle")
    db_historico = cfg.get("INFLUXDB_HISTORICAL_DATABASE", "fixture2030_historico")
    tabla = cfg.get("INFLUX_TABLA_DETALLE", "estadisticas_equipo")
    tabla_hist = cfg.get("INFLUX_TABLA_HISTORICO", "resumen_equipo_minuto")
    partido = cfg.get("INFLUX_PARTIDO_DEMO", "PAR-0001")
    desde = cfg.get("INFLUX_DESDE", "2030-06-13T20:00:00Z")
    hasta = cfg.get("INFLUX_HASTA", "2030-06-13T20:01:00Z")
    timeout = cfg.timeout
    cliente = f"httpx {version_paquete('httpx')} (API HTTP v3)"
    objetivo = f"{url} db={db_detalle}"

    try:
        import httpx
    except ImportError as error:
        cadena = Cadena("InfluxDB", clasificar_error_red, redactar, "httpx", objetivo)
        cadena.omitir_todo(f"httpx no instalado: {error}", "herramienta_no_disponible",
                           [("protocolo", "/health"), ("operacion", "SQL")])
        return cadena.resultados

    def clasificar(error: BaseException) -> str:
        if isinstance(error, httpx.TimeoutException):
            return "timeout"
        return clasificar_error_red(error.__cause__ or error) if isinstance(error, httpx.RequestError) else clasificar_error_red(error)

    cadena = Cadena("InfluxDB", clasificar, redactar, cliente, objetivo)
    con_token = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    http = httpx.Client(base_url=url, timeout=timeout, trust_env=False)
    estado = {}

    def interpretar(r: httpx.Response, ok_msg: str) -> tuple[str, str, str]:
        cuerpo = r.text[:160].replace("\n", " ")
        if r.status_code == 401:
            return FALLA, "auth_fallida", f"HTTP 401: token rechazado ({cuerpo})"
        if r.status_code == 403:
            return FALLA, "sin_permiso", f"HTTP 403: token sin permisos ({cuerpo})"
        if r.status_code == 404 or ("not found" in r.text.lower() and "database" in r.text.lower()):
            return FALLA, "contexto_inexistente", f"HTTP {r.status_code}: {cuerpo}"
        if r.status_code >= 400:
            return FALLA, "error_driver", f"HTTP {r.status_code}: {cuerpo}"
        return OK, "ok", ok_msg

    def sql(db: str, q: str, params: dict | None = None) -> httpx.Response:
        body = {"db": db, "q": q, "format": "json"}
        if params:
            body["params"] = params
        return http.post("/api/v3/query_sql", json=body, headers=con_token)

    try:
        def health():
            r = http.get("/health")
            estado["health_sin_token"] = r.status_code
            if r.status_code == 200:
                return OK, "health_ok", f"GET /health sin token -> 200 ({r.text.strip()[:40]})"
            if r.status_code == 401:
                return OK, "health_requiere_token", "GET /health sin token -> 401: el servicio HTTP responde y exige token"
            return FALLA, "protocolo_inesperado", f"GET /health -> HTTP {r.status_code}"

        cadena.paso(
            "protocolo", "GET /health (sin token)", health,
            "¿El endpoint HTTP de salud responde?",
            "Que el token sea válido ni que exista la database.",
        )

        def autenticacion():
            if not token:
                return FALLA, "auth_requerida_sin_credencial", "INFLUXDB_TOKEN vacío"
            r = http.get("/health", headers=con_token)
            estado_, clase, detalle = interpretar(r, "GET /health con token -> 200: token aceptado (valor oculto)")
            return estado_, ("autenticado" if estado_ == OK else clase), detalle

        cadena.paso(
            "autenticacion", "GET /health con token Bearer", autenticacion,
            "¿El servidor acepta el token configurado?",
            "Que el token tenga permiso sobre la database ni que la database exista.",
        )

        def token_invalido():
            r = http.get("/health", headers={"Authorization": "Bearer token-invalido-diagnostico"})
            if r.status_code == 401:
                return OK, "auth_fallida", "token inválido -> 401: el servidor diferencia token válido de inválido"
            if estado.get("health_sin_token") == 200:
                return ADVERTENCIA, "health_sin_autorizacion", (
                    f"/health no exige token (HTTP {r.status_code}); la validación del token se hace con la consulta SQL"
                )
            return ADVERTENCIA, "respuesta_inesperada", f"token inválido -> HTTP {r.status_code}"

        cadena.paso(
            "autenticacion", f"{NEGATIVA}: token inválido", token_invalido,
            "¿Un token inválido produce un rechazo identificable?",
            "-", requerida=False,
        )

        def contexto():
            r = http.get("/api/v3/configure/database", params={"format": "json"}, headers=con_token)
            if r.status_code in (404, 405):
                r2 = sql(db_detalle, "SHOW TABLES")
                return interpretar(r2, f"database '{db_detalle}' responde a SHOW TABLES")
            est, clase, detalle = interpretar(r, "")
            if est != OK:
                return est, clase, detalle
            nombres = set()
            try:
                for item in r.json():
                    nombres.add(item.get("iox::database") or item.get("name") or str(item))
            except Exception:
                nombres = set()
            faltan = [d for d in (db_detalle, db_historico) if d not in nombres]
            if faltan:
                return FALLA, "contexto_inexistente", f"no existen: {', '.join(faltan)} (existen: {', '.join(sorted(nombres)) or '-'})"
            return OK, "contexto_ok", f"databases presentes: {db_detalle}, {db_historico}"

        cadena.paso(
            "contexto", "databases configuradas", contexto,
            "¿Existen las databases de detalle e histórico configuradas?",
            "Que haya puntos en la ventana consultada.",
        )

        def autorizacion():
            r = sql(db_detalle, "SELECT 1 AS ok")
            return interpretar(r, f"query_sql permitido sobre '{db_detalle}'")

        cadena.paso(
            "autorizacion", f"SELECT 1 sobre {db_detalle}", autorizacion,
            "¿El token puede consultar la database de detalle?",
            "Que la tabla tenga datos.",
        )

        consulta = (
            f"SELECT COUNT(*) AS puntos, MIN(time) AS primero, MAX(time) AS ultimo FROM {tabla} "
            "WHERE partido_id = $partido_id AND time >= $desde AND time < $hasta"
        )

        def operacion():
            r = sql(db_detalle, consulta, {"partido_id": partido, "desde": desde, "hasta": hasta})
            est, clase, detalle = interpretar(r, "")
            if est != OK:
                return est, clase, detalle
            filas = r.json()
            puntos = filas[0].get("puntos", 0) if filas else 0
            if not puntos:
                return ADVERTENCIA, "vacio_valido", f"ventana [{desde}, {hasta}) sin puntos para {partido}"
            return OK, "lectura_ok", (
                f"{tabla}: partido_id={partido}, rango [{desde}, {hasta}), agregación COUNT/MIN/MAX -> "
                f"{puntos} puntos (primero={filas[0].get('primero')}, último={filas[0].get('ultimo')})"
            )

        cadena.paso(
            "operacion", f"SQL acotado {tabla} (1 minuto)", operacion,
            "¿Se puede ejecutar una consulta temporal acotada con agregación?",
            "Rendimiento con ventanas grandes o concurrencia (Hito 12).",
        )

        def historico():
            r = sql(
                db_historico,
                f"SELECT COUNT(*) AS filas FROM {tabla_hist} WHERE partido_id = $partido_id "
                "AND time >= $desde AND time < $hasta",
                {"partido_id": partido, "desde": desde, "hasta": "2030-06-13T20:31:00Z"},
            )
            est, clase, detalle = interpretar(r, "")
            if est != OK:
                return est, clase, detalle
            filas = r.json()
            return OK, "lectura_ok", f"{db_historico}.{tabla_hist}: {filas[0].get('filas', 0) if filas else 0} resúmenes en 31 minutos"

        cadena.paso(
            "operacion", f"SQL acotado {tabla_hist} (resúmenes 15 min)", historico,
            "¿La database histórica (downsampling) es consultable?",
            "-", requerida=False,
        )

        def ventana_vacia():
            r = sql(db_detalle, consulta, {"partido_id": partido, "desde": "2031-01-01T00:00:00Z", "hasta": "2031-01-01T00:01:00Z"})
            est, clase, detalle = interpretar(r, "")
            if est != OK:
                return ADVERTENCIA, clase, detalle
            filas = r.json()
            puntos = filas[0].get("puntos", 0) if filas else 0
            return OK, "vacio_valido", f"ventana 2031-01-01 sin datos: {puntos} puntos y HTTP 200 (ausencia de puntos ≠ error)"

        cadena.paso(
            "operacion", f"{NEGATIVA}: ventana sin puntos", ventana_vacia,
            "¿Una ventana sin datos se distingue de un error?",
            "-", requerida=False,
        )

        def db_inexistente():
            r = sql("fixture2030_diag_inexistente", "SELECT 1")
            est, clase, detalle = interpretar(r, "")
            if clase == "contexto_inexistente":
                return OK, clase, detalle
            return ADVERTENCIA, clase, f"respuesta distinta a la esperada: {detalle or r.status_code}"

        cadena.paso(
            "contexto", f"{NEGATIVA}: database inexistente", db_inexistente,
            "¿Una database inexistente se distingue de token inválido y de servicio caído?",
            "-", requerida=False,
        )
    finally:
        http.close()

    return cadena.resultados


# ==========================================================================
# InterSystems IRIS
# ==========================================================================

def evaluar_iris(cfg: Config, redactar: Redactor) -> list[Resultado]:
    host = cfg.get("IRIS_HOST", "127.0.0.1")
    port = cfg.get_int("IRIS_PORT", 1972)
    portal_port = cfg.get_int("IRIS_PORTAL_PORT", 52773)
    namespace = cfg.get("IRIS_NAMESPACE", "USER")
    usuario = cfg.get("IRIS_USERNAME", "")
    password = cfg.get("IRIS_PASSWORD", "")
    partido = cfg.get("IRIS_PARTIDO_DEMO", "PAR-0001")
    timeout = max(1, int(round(cfg.timeout)))
    cliente = f"intersystems-irispython {version_paquete('intersystems_irispython')} (DB-API)"
    objetivo = f"{host}:{port}/{namespace}"

    try:
        import httpx
        import iris.dbapi as iris_dbapi
    except ImportError as error:
        cadena = Cadena("InterSystems IRIS", clasificar_error_red, redactar, "iris", objetivo)
        cadena.omitir_todo(f"driver no instalado: {error}", "herramienta_no_disponible",
                           [("protocolo", "Superserver"), ("operacion", "SQL")])
        return cadena.resultados

    def clasificar_mensaje(texto: str) -> str:
        t = texto.lower()
        # IRIS informa "Access Denied" dentro de un COMMUNICATION LINK ERROR:
        # el Superserver respondió, así que no es un problema de red.
        if "access denied" in t or "authentication" in t or "invalid password" in t:
            return "auth_fallida"
        if "communication link" in t or "failed to connect" in t:
            return "connection_refused"
        if "namespace" in t:
            return "contexto_inexistente"
        if "privilege" in t or "not authorized" in t:
            return "sin_permiso"
        if "table" in t and "not found" in t:
            return "tabla_inexistente"
        if "timeout" in t:
            return "timeout"
        return "error_driver"

    def clasificar(error: BaseException) -> str:
        clase = clasificar_mensaje(str(error))
        return clase if clase != "error_driver" else clasificar_error_red(error)

    cadena = Cadena("InterSystems IRIS", clasificar, redactar, cliente, objetivo)
    estado: dict = {}

    def portal():
        r = httpx.get(
            f"http://{host}:{portal_port}/csp/sys/UtilHome.csp",
            timeout=cfg.timeout,
            follow_redirects=False,
            trust_env=False,
        )
        return OK, "portal_http_ok", (
            f"Management Portal respondió HTTP {r.status_code} (200/302/401 indican portal activo; no usa la identidad de la API)"
        )

    cadena.paso(
        "protocolo", "portal HTTP (Management Portal)", portal,
        "¿Responde el portal web de IRIS?",
        "Nada sobre el Superserver (1972) que usa la API: el portal puede estar accesible y el Superserver no.",
        requerida=False, objetivo=f"{host}:{portal_port}", cliente="httpx", necesita_cadena=False,
    )

    # El driver DB-API realiza handshake, autenticación y selección de
    # namespace en una única llamada a connect(). Se ejecuta una vez y su
    # resultado se descompone por capa según el tipo de error.
    def conectar():
        inicio = time.perf_counter()
        try:
            estado["conn"] = iris_dbapi.connect(host, port, namespace, usuario, password, timeout=timeout)
            estado["error"] = None
        except Exception as error:  # noqa: BLE001
            estado["conn"] = None
            estado["error"] = error
            estado["clase"] = clasificar(error)
        estado["ms"] = (time.perf_counter() - inicio) * 1000

    conectar()

    def capa_desde_connect(capa: str):
        def fn():
            error = estado["error"]
            nota = f"inferido del mismo connect() ({estado['ms']:.1f} ms)"
            if error is None:
                mensajes = {
                    "protocolo": "handshake con el Superserver completado",
                    "autenticacion": "credenciales aceptadas (valores ocultos)",
                    "contexto": f"namespace '{namespace}' seleccionado",
                }
                return OK, f"{capa}_ok", f"{mensajes[capa]}; {nota}"
            clase = estado["clase"]
            orden = {"connection_refused": 0, "timeout": 0, "error_driver": 0, "host_no_resuelto": 0,
                     "auth_fallida": 1, "contexto_inexistente": 2}
            nivel_falla = orden.get(clase, 0)
            nivel_capa = {"protocolo": 0, "autenticacion": 1, "contexto": 2}[capa]
            if nivel_capa < nivel_falla:
                return OK, f"{capa}_ok", f"superada: el error ocurrió en una capa posterior ({clase}); {nota}"
            return FALLA, clase, f"{type(error).__name__}: {error}; {nota}"
        return fn

    cadena.paso(
        "protocolo", "handshake Superserver (DB-API connect)", capa_desde_connect("protocolo"),
        "¿El puerto del Superserver acepta el protocolo del driver?",
        "Que la identidad sea válida (se evalúa en la capa siguiente).",
    )
    cadena.paso(
        "autenticacion", "usuario/password en connect", capa_desde_connect("autenticacion"),
        "¿IRIS acepta la identidad configurada?",
        "Que el namespace exista o que la identidad pueda leer las clases.",
    )
    cadena.paso(
        "contexto", f"namespace {namespace}", capa_desde_connect("contexto"),
        "¿El namespace configurado existe y se seleccionó?",
        "Que las clases Fixture.* estén compiladas en ese namespace.",
    )

    try:
        def autorizacion():
            cur = estado["conn"].cursor()
            cur.setQueryTimeout(timeout)
            cur.execute(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = ?",
                ["Fixture"],
            )
            total = cur.fetchone()[0]
            cur.close()
            if not total:
                return FALLA, "tabla_inexistente", f"el namespace '{namespace}' no tiene tablas del esquema Fixture"
            return OK, "autorizado", f"metadato legible: {total} tablas/clases proyectadas en el esquema Fixture"

        cadena.paso(
            "autorizacion", "lectura de metadatos (INFORMATION_SCHEMA)", autorizacion,
            "¿La identidad puede leer el catálogo y existen las clases del Fixture?",
            "Que exista el partido de demostración.",
        )

        def operacion():
            cur = estado["conn"].cursor()
            cur.setQueryTimeout(timeout)
            cur.execute("SELECT Codigo, Estado FROM Fixture.Partido WHERE Codigo = ?", [partido])
            filas = cur.fetchall()
            cur.execute("SELECT COUNT(*) FROM Fixture.Partido")
            total = cur.fetchone()[0]
            cur.close()
            if not filas:
                return ADVERTENCIA, "recurso_inexistente", f"conexión correcta pero {partido} no existe (partidos={total})"
            return OK, "lectura_ok", f"Fixture.Partido {partido}: estado={filas[0][1]}; total partidos={total}"

        cadena.paso(
            "operacion", f"lectura Fixture.Partido {partido}", operacion,
            "¿Se puede leer la entidad persistente que usa la API?",
            "Rendimiento con volumen (Hito 12).",
        )

        def inexistente():
            cur = estado["conn"].cursor()
            cur.setQueryTimeout(timeout)
            cur.execute("SELECT Codigo FROM Fixture.Partido WHERE Codigo = ?", ["PAR-9999"])
            filas = cur.fetchall()
            cur.close()
            if not filas:
                return OK, "recurso_inexistente", "PAR-9999: 0 filas sin error (objeto inexistente ≠ Superserver inaccesible)"
            return ADVERTENCIA, "respuesta_inesperada", "PAR-9999 existe"

        cadena.paso(
            "operacion", f"{NEGATIVA}: objeto inexistente PAR-9999", inexistente,
            "¿Un objeto inexistente se distingue de una falla de conexión?",
            "-", requerida=False,
        )
    finally:
        if estado.get("conn") is not None:
            try:
                estado["conn"].close()
            except Exception:
                pass

    def namespace_incorrecto():
        try:
            conn = iris_dbapi.connect(host, port, "NSDIAGINEXISTENTE", usuario, password, timeout=timeout)
            conn.close()
        except Exception as error:  # noqa: BLE001
            clase = clasificar_mensaje(str(error))
            if clase == "contexto_inexistente":
                return OK, clase, f"error esperado: {type(error).__name__}: {error}"
            if clase == "auth_fallida" and estado.get("error") is None:
                return OK, "contexto_inexistente", (
                    "IRIS respondió 'Access Denied' al pedir un namespace inexistente: por seguridad usa el mismo "
                    "mensaje que para una credencial inválida. Como las mismas credenciales funcionaron en "
                    f"'{namespace}', el rechazo se atribuye al namespace. Distinto de Superserver inaccesible, "
                    "que no llega a responder."
                )
            return ADVERTENCIA, clase, f"error distinto al esperado: {type(error).__name__}: {error}"
        return ADVERTENCIA, "respuesta_inesperada", "IRIS aceptó un namespace inexistente"

    cadena.paso(
        "contexto", f"{NEGATIVA}: namespace incorrecto", namespace_incorrecto,
        "¿Un namespace mal configurado produce un error distinto a credencial inválida o Superserver caído?",
        "-", requerida=False,
    )

    return cadena.resultados


# ==========================================================================
# Clientes de línea de comandos dentro de los contenedores (opcional)
# ==========================================================================

def evaluar_cli(cfg: Config, productos: list[str], redactar: Redactor) -> list[Resultado]:
    resultados = []
    disponible = docker_disponible()
    activos = docker_contenedores() if disponible else {}

    comandos = {
        "mongodb": lambda: [
            "mongosh", "--quiet",
            "--username", cfg.get("MONGODB_USERNAME", ""),
            "--password", cfg.get("MONGODB_PASSWORD", ""),
            "--authenticationDatabase", cfg.get("MONGODB_AUTH_SOURCE", "admin"),
            cfg.get("MONGODB_DATABASE", "fixture2030"),
            "--eval", "print('ping=' + db.runCommand({ping:1}).ok + ' equipos=' + db.equipos.estimatedDocumentCount())",
        ],
        "neo4j": lambda: [
            "cypher-shell", "-a", "bolt://localhost:7687",
            "-u", cfg.get("NEO4J_USERNAME", ""), "-p", cfg.get("NEO4J_PASSWORD", ""),
            "-d", cfg.get("NEO4J_DATABASE", "neo4j"), "--format", "plain",
            "MATCH (e:Equipo) RETURN count(e) AS equipos",
        ],
        "cassandra": lambda: [
            "cqlsh", "-e",
            f"SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name = '{cfg.get('CASSANDRA_KEYSPACE')}';",
        ],
        "redis": lambda: ["redis-cli", "-n", str(cfg.get_int("REDIS_DATABASE", 0)), "PING"],
        "influxdb": lambda: [
            "influxdb3", "query", "--host", "http://127.0.0.1:8181",
            "--database", cfg.get("INFLUXDB_DETAIL_DATABASE", ""),
            "--token", cfg.get("INFLUXDB_TOKEN", ""),
            "SELECT 1 AS ok",
        ],
        "iris": lambda: ["iris", "list"],
    }
    nombres_cli = {
        "mongodb": "mongosh", "neo4j": "cypher-shell", "cassandra": "cqlsh",
        "redis": "redis-cli", "influxdb": "influxdb3 CLI", "iris": "iris list",
    }

    for clave in productos:
        spec = PRODUCTOS[clave]
        contenedor = resolver_contenedor(cfg, clave, activos) if disponible else None
        base = dict(
            producto=spec["nombre"],
            capa="operacion",
            prueba=f"cliente nativo CLI {nombres_cli[clave]} dentro del contenedor",
            objetivo=contenedor or cfg.contenedor(clave),
            origen=f"contenedor {contenedor or cfg.contenedor(clave)} (no es el origen de la API)",
            cliente=nombres_cli[clave],
            requerida=False,
            pregunta="¿El producto responde a su cliente oficial desde dentro de su propio contenedor?",
            no_concluye=(
                "Que la API pueda conectarse: el CLI usa localhost dentro del contenedor y puertos internos, "
                "un origen distinto al de la API."
            ),
        )
        if not disponible or not contenedor:
            resultados.append(Resultado(
                **base, estado=SKIP, clasificacion="herramienta_no_disponible",
                detalle="Docker CLI no disponible" if not disponible else "contenedor no encontrado en ejecución",
            ))
            continue

        inicio = time.perf_counter()
        try:
            out = subprocess.run(
                ["docker", "exec", contenedor, *comandos[clave]()],
                capture_output=True, text=True, timeout=max(15, cfg.timeout * 5),
            )
            salida = redactar((out.stdout + " " + out.stderr).strip().replace("\n", " | "))[:400]
            rc = out.returncode
        except subprocess.TimeoutExpired:
            salida, rc = "el cliente no terminó dentro del límite", 124
        dur = round((time.perf_counter() - inicio) * 1000, 2)

        if rc == 0:
            estado, clase = OK, "cli_ok"
        elif "executable file not found" in salida or "not found" in salida.lower() and rc == 127:
            estado, clase = SKIP, "herramienta_no_disponible"
        elif rc == 124:
            estado, clase = FALLA, "timeout"
        else:
            texto = salida.lower()
            if "auth" in texto or "unauthorized" in texto or "access denied" in texto:
                clase = "auth_fallida"
            elif "refused" in texto or "unable to connect" in texto:
                clase = "connection_refused"
            else:
                clase = "error_driver"
            estado = FALLA

        resultados.append(completar_diagnostico(Resultado(
            **base, estado=estado, clasificacion=clase, detalle=f"rc={rc}; {salida}", duracion_ms=dur,
        )))

    return resultados


# ==========================================================================
# Orquestación
# ==========================================================================

EVALUADORES = {
    "mongodb": evaluar_mongodb,
    "neo4j": evaluar_neo4j,
    "cassandra": evaluar_cassandra,
    "redis": evaluar_redis,
    "influxdb": evaluar_influxdb,
    "iris": evaluar_iris,
}


def evaluar(
    cfg: Config,
    productos: list[str],
    redactar: Redactor,
    permitir_escritura: bool = True,
    usar_cli: bool = False,
) -> list[Resultado]:
    resultados: list[Resultado] = []
    for clave in productos:
        spec = PRODUCTOS[clave]
        faltantes = [v for v in spec["requeridas"] if not cfg.definida(v)]
        if faltantes:
            resultados.append(completar_diagnostico(Resultado(
                producto=spec["nombre"], capa="configuracion", prueba="variables requeridas presentes",
                objetivo="-", estado=FALLA, clasificacion="variables_faltantes",
                detalle=f"faltan: {', '.join(faltantes)}; no se ejecutan las pruebas nativas",
                cliente="lectura de configuración",
            )))
            continue
        try:
            if clave == "redis":
                resultados += evaluar_redis(cfg, redactar, permitir_escritura)
            else:
                resultados += EVALUADORES[clave](cfg, redactar)
        except Exception as error:  # noqa: BLE001 - un producto no debe cortar el resto (RNF13)
            resultados.append(completar_diagnostico(Resultado(
                producto=spec["nombre"], capa="protocolo", prueba="evaluación del producto",
                objetivo="-", estado=FALLA, clasificacion="error_driver",
                detalle=redactar(f"{type(error).__name__}: {error}"),
            )))
    if usar_cli:
        resultados += evaluar_cli(cfg, productos, redactar)
    return resultados


def main(argv: list[str] | None = None) -> int:
    preparar_consola()
    parser = argparse.ArgumentParser(description="Hito 11 - clientes nativos por capa")
    parser.add_argument("--producto", default="todos", choices=["todos", *PRODUCTOS])
    parser.add_argument("--set", action="append", default=[], metavar="CLAVE=VALOR")
    parser.add_argument("--etiqueta", default="")
    parser.add_argument("--sin-escritura", action="store_true",
                        help="no crear la clave diag:hito11:* en Redis")
    parser.add_argument("--cli", action="store_true",
                        help="ejecutar también los clientes CLI dentro de los contenedores")
    args = parser.parse_args(argv)

    cfg = Config(parse_overrides(args.set))
    redactar = Redactor(cfg.secretos())
    productos = list(PRODUCTOS) if args.producto == "todos" else [args.producto]

    contexto = contexto_ejecucion(cfg, "nativos")
    print("=== HITO 11 - CLIENTES NATIVOS POR CAPA ===")
    print(f"Fecha: {contexto['fecha']} | Origen: {contexto['origen_de_las_pruebas']} | Timeout: {cfg.timeout} s")
    print()

    resultados = evaluar(cfg, productos, redactar, not args.sin_escritura, args.cli)
    for r in resultados:
        imprimir_resultado(r)
    imprimir_resumen(resultados)

    txt, _ = escribir_evidencia("resultados_clientes", contexto, resultados, redactar, args.etiqueta)
    print(f"\nEvidencia: {txt}")
    return 1 if any(r.estado == FALLA and r.requerida for r in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())
