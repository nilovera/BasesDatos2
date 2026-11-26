import re
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Header, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from .cassandra_client import close_cassandra_client, get_cassandra_session
from .cassandra_service import CassandraCommentService
from .config import settings
from .datamart_client import close_datamart_pool, datamart_connection
from .datamart_service import DataMartService
from .database import close_client, get_client
from .errors import DomainError
from .influx_client import close_influx_client, get_influx_client
from .influx_service import InfluxTelemetryService
from .metrics import (
    CACHE_READS,
    COMMENT_OPERATIONS,
    DEPENDENCY_UP,
    EVENTS_CONFIRMED,
    GRAPH_OPERATIONS,
    DATAMART_OPERATIONS,
    HTTP_DURATION,
    HTTP_REQUESTS,
    IDEMPOTENCY_REPLAYS,
    SESSION_OPERATIONS,
    TELEMETRY_OPERATIONS,
)
from .models import (
    AgregacionResponse,
    EventoCommand,
    EventoConfirmado,
    ComentarioCreate,
    ComentarioCreado,
    CaminoGrafoResponse,
    DataMartRefreshResponse,
    DataMartSummary,
    GrafoResumen,
    HealthResponse,
    GoalsByTeamResponse,
    ModeracionComentario,
    ModeracionResponse,
    EstadisticasEquipoBatch,
    MapaCalorResponse,
    PaginaComentarios,
    PaginaEventos,
    PaginaPosiciones,
    PaginaPelota,
    PaginaResumenesEquipo,
    PartidoResponse,
    PosicionesBatch,
    PelotaBatch,
    RecomendacionesJugadoresResponse,
    RivalesResponse,
    SesionCreate,
    SesionRenovacion,
    SesionResponse,
    TelemetryWriteResponse,
    SimulacionCrear,
    SimulacionEstado,
    SimulacionVelocidad,
)
from .neo4j_client import close_neo4j_client, get_neo4j_client
from .neo4j_service import Neo4jGraphService
from .redis_client import RedisError, close_redis_client, get_redis_client
from .redis_service import RedisService
from .repository import MongoRepository
from .simulation_worker import start_simulation_worker, stop_simulation_worker
from .simulator_engine import build_plan, select_lineup


PARTIDO_ID = re.compile(r"^PAR-[0-9]{4}$")
TEAM_ID = re.compile(r"^EQ-[0-9]{2}$")
PLAYER_ID = re.compile(r"^JUG-[0-9]{4}$")
USER_ID = re.compile(r"^USR-[0-9]{4}$")
COMMENT_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SESSION_ID = re.compile(
    r"^SES-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


@asynccontextmanager
async def lifespan(_app):
    start_simulation_worker()
    yield
    stop_simulation_worker()
    close_neo4j_client()
    close_datamart_pool()
    close_influx_client()
    close_cassandra_client()
    close_redis_client()
    close_client()


app = FastAPI(
    title="Fixture 2030 API",
    version="0.9.0",
    description="Plataforma operacional políglota y Data Mart analítico PostgreSQL para Fixture 2030.",
    lifespan=lifespan,
)
app.mount("/metrics", make_asgi_app())


def repository():
    return MongoRepository(get_client())


def redis_service():
    return RedisService(
        get_redis_client(),
        (RedisError,),
        settings.match_cache_ttl_seconds,
    )


def comment_service():
    return CassandraCommentService(get_cassandra_session())


def telemetry_service():
    return InfluxTelemetryService(
        get_influx_client(),
        settings.influxdb_detail_database,
        settings.influxdb_historical_database,
    )


def graph_service():
    return Neo4jGraphService(get_neo4j_client())


def datamart_service():
    return DataMartService(datamart_connection)


def request_id(request):
    return getattr(request.state, "request_id", str(uuid4()))


def validate_match_id(partido_id):
    if not PARTIDO_ID.fullmatch(partido_id):
        raise DomainError(400, "INVALID_MATCH_ID", "Formato de partidoId inválido")


def validate_team_id(team_id):
    if not TEAM_ID.fullmatch(team_id):
        raise DomainError(400, "INVALID_TEAM_ID", "Formato de equipoId inválido")


def validate_player_id(player_id):
    if not PLAYER_ID.fullmatch(player_id):
        raise DomainError(400, "INVALID_PLAYER_ID", "Formato de jugadorId inválido")


def validate_session_id(session_id):
    if not SESSION_ID.fullmatch(session_id):
        raise DomainError(400, "INVALID_SESSION_ID", "Formato de sesionId inválido")


def validate_user_id(user_id):
    if not USER_ID.fullmatch(user_id):
        raise DomainError(400, "INVALID_USER_ID", "Formato de usuarioId inválido")


def validate_comment_id(comment_id):
    if not COMMENT_ID.fullmatch(comment_id):
        raise DomainError(400, "INVALID_COMMENT_ID", "Formato de comentarioId inválido")


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    incoming_id = request.headers.get("X-Request-ID", "")
    request.state.request_id = incoming_id if 8 <= len(incoming_id) <= 128 else str(uuid4())
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    if not request.url.path.startswith("/metrics"):
        route = request.scope.get("route")
        route_name = getattr(route, "path", "unmatched")
        HTTP_REQUESTS.labels(request.method, route_name, response.status_code).inc()
        HTTP_DURATION.labels(request.method, route_name).observe(
            time.perf_counter() - started
        )
    return response


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, error: DomainError):
    return JSONResponse(
        status_code=error.status,
        content={
            "codigo": error.code,
            "mensaje": error.message,
            "requestId": request_id(request),
            "detalles": error.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, error: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "codigo": "INVALID_REQUEST",
            "mensaje": "La solicitud no cumple el contrato",
            "requestId": request_id(request),
            "detalles": {"errores": jsonable_encoder(error.errors())},
        },
    )


@app.get("/health", response_model=HealthResponse)
def health():
    mongo_status = repository().health_status()
    redis_status = redis_service().health()
    try:
        cassandra_status = comment_service().health()
    except Exception:
        cassandra_status = "DOWN"
    try:
        influxdb_status = telemetry_service().health()
    except Exception:
        influxdb_status = "DOWN"
    try:
        neo4j_status = graph_service().health()
    except Exception:
        neo4j_status = "DOWN"
    try:
        datamart_status = datamart_service().health()
    except Exception:
        datamart_status = "DOWN"
    DEPENDENCY_UP.labels("mongodb").set(1 if mongo_status == "PRIMARY" else 0)
    DEPENDENCY_UP.labels("redis").set(1 if redis_status == "UP" else 0)
    DEPENDENCY_UP.labels("cassandra").set(1 if cassandra_status == "UP" else 0)
    DEPENDENCY_UP.labels("influxdb").set(1 if influxdb_status == "UP" else 0)
    DEPENDENCY_UP.labels("neo4j").set(1 if neo4j_status == "UP" else 0)
    DEPENDENCY_UP.labels("datamart").set(1 if datamart_status == "UP" else 0)
    return {
        "service": "fixture2030-api",
        "status": "UP"
        if mongo_status == "PRIMARY"
        and redis_status == "UP"
        and cassandra_status == "UP"
        and influxdb_status == "UP"
        and neo4j_status == "UP"
        and datamart_status == "UP"
        else "DEGRADED",
        "mongodb": mongo_status,
        "redis": redis_status,
        "cassandra": cassandra_status,
        "influxdb": influxdb_status,
        "neo4j": neo4j_status,
        "datamart": datamart_status,
    }


@app.get(
    "/api/v1/partidos/{partidoId}",
    response_model=PartidoResponse,
    responses={
        200: {
            "headers": {
                "X-Cache": {
                    "description": "Resultado Cache-Aside: HIT, MISS o BYPASS",
                    "schema": {"type": "string", "enum": ["HIT", "MISS", "BYPASS"]},
                }
            }
        },
        400: {"description": "Identificador inválido"},
        404: {"description": "Partido inexistente"},
        503: {"description": "MongoDB no disponible"},
    },
)
def get_match(partidoId: str, response: Response):
    validate_match_id(partidoId)
    result = redis_service().get_match(
        partidoId, lambda: repository().get_match(partidoId)
    )
    response.headers["X-Cache"] = result.result
    CACHE_READS.labels(result.result).inc()
    return result.value


@app.get("/api/v1/partidos/{partidoId}/eventos", response_model=PaginaEventos)
def get_events(
    partidoId: str,
    desde_secuencia: int = Query(0, alias="desdeSecuencia", ge=0),
    limite: int = Query(50, ge=1, le=100),
):
    validate_match_id(partidoId)
    return repository().list_events(partidoId, desde_secuencia, limite)


@app.post(
    "/api/v1/partidos/{partidoId}/eventos",
    response_model=EventoConfirmado,
    status_code=201,
    responses={
        200: {
            "model": EventoConfirmado,
            "headers": {
                "Idempotency-Replayed": {
                    "schema": {"type": "boolean", "const": True}
                }
            },
        },
        400: {"description": "Comando inválido"},
        404: {"description": "Partido o evento inexistente"},
        409: {"description": "Conflicto de idempotencia, versión o estado"},
        422: {"description": "Contrato inválido"},
        503: {"description": "MongoDB no disponible"},
    },
)
def post_event(
    partidoId: str,
    event: EventoCommand,
    response: Response,
    idempotency_key: str = Header(
        alias="Idempotency-Key", min_length=16, max_length=128
    ),
):
    validate_match_id(partidoId)
    payload = event.model_dump(by_alias=True, mode="json")
    result = repository().register_event(
        partidoId, idempotency_key, payload, event.ocurrido_en
    )
    response.status_code = result.status
    response.headers["Idempotency-Replayed"] = str(result.replayed).lower()
    if result.replayed:
        IDEMPOTENCY_REPLAYS.inc()
    else:
        EVENTS_CONFIRMED.labels(payload["tipo"]).inc()
    return result.body


@app.post(
    "/api/v1/simulaciones",
    response_model=SimulacionEstado,
    status_code=201,
    responses={404: {"description": "Partido base inexistente"}, 503: {"description": "MongoDB no disponible"}},
)
def create_simulation(command: SimulacionCrear):
    context = repository().simulation_context(command.partido_base_id)
    rosters = {
        team: [player for player in context["jugadores"] if player["equipoId"] == team]
        for team in (context["localId"], context["visitanteId"])
    }
    local_starters, local_bench = select_lineup(rosters[context["localId"]])
    visitor_starters, visitor_bench = select_lineup(rosters[context["visitanteId"]])
    plan = build_plan(
        command.semilla,
        context["localId"],
        context["visitanteId"],
        rosters,
        datetime.now(timezone.utc),
    )
    lineups = {
        "local": {
            "titulares": [player["jugadorId"] for player in local_starters],
            "suplentes": [player["jugadorId"] for player in local_bench],
        },
        "visitante": {
            "titulares": [player["jugadorId"] for player in visitor_starters],
            "suplentes": [player["jugadorId"] for player in visitor_bench],
        },
    }
    return repository().create_simulation(
        command.partido_base_id, command.semilla, command.velocidad, plan, lineups
    )


@app.get("/api/v1/simulaciones/{simulacionId}", response_model=SimulacionEstado)
def get_simulation(simulacionId: str):
    return repository().get_simulation(simulacionId)


def _control_simulation(simulation_id, action, speed=None):
    result = repository().control_simulation(simulation_id, action, speed)
    try:
        get_redis_client().hset(
            f"marcador:partido:{result['partidoId']}",
            mapping={
                "simulacionEstado": result["estado"],
                "velocidad": result["velocidad"],
                "segundoPartido": result["segundoPartido"],
                "minuto": result["minutoPartido"],
            },
        )
    except RedisError:
        pass
    return result


@app.post("/api/v1/simulaciones/{simulacionId}/iniciar", response_model=SimulacionEstado)
def start_simulation(simulacionId: str):
    return _control_simulation(simulacionId, "INICIAR")


@app.post("/api/v1/simulaciones/{simulacionId}/pausar", response_model=SimulacionEstado)
def pause_simulation(simulacionId: str):
    return _control_simulation(simulacionId, "PAUSAR")


@app.post("/api/v1/simulaciones/{simulacionId}/reanudar", response_model=SimulacionEstado)
def resume_simulation(simulacionId: str):
    return _control_simulation(simulacionId, "REANUDAR")


@app.patch("/api/v1/simulaciones/{simulacionId}/velocidad", response_model=SimulacionEstado)
def change_simulation_speed(simulacionId: str, command: SimulacionVelocidad):
    return _control_simulation(simulacionId, "VELOCIDAD", command.velocidad)


@app.post(
    "/api/v1/sesiones",
    response_model=SesionResponse,
    status_code=201,
    responses={503: {"description": "Redis no disponible"}},
)
def create_session(command: SesionCreate):
    try:
        result = redis_service().create_session(
            command.usuario_id, command.rol, command.ttl_segundos
        )
        SESSION_OPERATIONS.labels("create", "OK").inc()
        return result
    except DomainError:
        SESSION_OPERATIONS.labels("create", "ERROR").inc()
        raise


@app.get(
    "/api/v1/sesiones/{sesionId}",
    response_model=SesionResponse,
    responses={
        404: {"description": "Sesión inexistente o expirada"},
        503: {"description": "Redis no disponible"},
    },
)
def get_session(sesionId: str):
    validate_session_id(sesionId)
    try:
        result = redis_service().get_session(sesionId)
        SESSION_OPERATIONS.labels("read", "OK").inc()
        return result
    except DomainError:
        SESSION_OPERATIONS.labels("read", "ERROR").inc()
        raise


@app.post(
    "/api/v1/sesiones/{sesionId}/renovacion",
    response_model=SesionResponse,
    responses={
        404: {"description": "Sesión inexistente o expirada"},
        503: {"description": "Redis no disponible"},
    },
)
def renew_session(sesionId: str, command: SesionRenovacion):
    validate_session_id(sesionId)
    try:
        result = redis_service().renew_session(sesionId, command.ttl_segundos)
        SESSION_OPERATIONS.labels("renew", "OK").inc()
        return result
    except DomainError:
        SESSION_OPERATIONS.labels("renew", "ERROR").inc()
        raise


@app.delete(
    "/api/v1/sesiones/{sesionId}",
    status_code=204,
    responses={
        404: {"description": "Sesión inexistente o expirada"},
        503: {"description": "Redis no disponible"},
    },
)
def delete_session(sesionId: str):
    validate_session_id(sesionId)
    try:
        redis_service().delete_session(sesionId)
        SESSION_OPERATIONS.labels("delete", "OK").inc()
    except DomainError:
        SESSION_OPERATIONS.labels("delete", "ERROR").inc()
        raise
    return Response(status_code=204)


@app.post(
    "/api/v1/partidos/{partidoId}/comentarios",
    response_model=ComentarioCreado,
    status_code=201,
    responses={
        200: {
            "model": ComentarioCreado,
            "headers": {"Idempotency-Replayed": {"schema": {"type": "boolean"}}},
        },
        404: {"description": "Partido inexistente"},
        409: {"description": "Conflicto de idempotencia"},
        503: {"description": "MongoDB o Cassandra no disponible"},
    },
)
def publish_comment(
    partidoId: str,
    command: ComentarioCreate,
    response: Response,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=16, max_length=128),
):
    validate_match_id(partidoId)
    repository().get_match(partidoId)
    try:
        result = comment_service().publish(
            partidoId, command.usuario_id, command.contenido, idempotency_key
        )
        replayed = result["repetido"]
        response.status_code = 200 if replayed else 201
        response.headers["Idempotency-Replayed"] = str(replayed).lower()
        COMMENT_OPERATIONS.labels("publish", "REPLAY" if replayed else "OK").inc()
        return result
    except DomainError:
        COMMENT_OPERATIONS.labels("publish", "ERROR").inc()
        raise


@app.get(
    "/api/v1/partidos/{partidoId}/comentarios",
    response_model=PaginaComentarios,
    responses={503: {"description": "Cassandra no disponible"}},
)
def list_match_comments(
    partidoId: str,
    bucket: str = Query(pattern=r"^[0-9]{12}$"),
    antes_de: str | None = Query(
        None,
        alias="antesDe",
        description="Cursor opaco devuelto por siguienteCursor; no es una fecha editable",
    ),
    limite: int = Query(50, ge=1, le=100),
    incluir_ocultos: bool = Query(False, alias="incluirOcultos"),
):
    validate_match_id(partidoId)
    try:
        result = comment_service().list_by_match(
            partidoId, bucket, antes_de, limite, incluir_ocultos
        )
        COMMENT_OPERATIONS.labels("read_match", "OK").inc()
        return result
    except DomainError:
        COMMENT_OPERATIONS.labels("read_match", "ERROR").inc()
        raise


@app.get(
    "/api/v1/usuarios/{usuarioId}/comentarios",
    response_model=PaginaComentarios,
    responses={503: {"description": "Cassandra no disponible"}},
)
def list_user_comments(
    usuarioId: str,
    bucket: str = Query(pattern=r"^[0-9]{8}$"),
    antes_de: str | None = Query(
        None,
        alias="antesDe",
        description="Cursor opaco devuelto por siguienteCursor; no es una fecha editable",
    ),
    limite: int = Query(50, ge=1, le=100),
    incluir_ocultos: bool = Query(False, alias="incluirOcultos"),
):
    validate_user_id(usuarioId)
    try:
        result = comment_service().list_by_user(
            usuarioId, bucket, antes_de, limite, incluir_ocultos
        )
        COMMENT_OPERATIONS.labels("read_user", "OK").inc()
        return result
    except DomainError:
        COMMENT_OPERATIONS.labels("read_user", "ERROR").inc()
        raise


@app.patch(
    "/api/v1/comentarios/{comentarioId}/moderacion",
    response_model=ModeracionResponse,
    responses={
        404: {"description": "Comentario inexistente"},
        503: {"description": "Cassandra no disponible"},
    },
)
def moderate_comment(comentarioId: str, command: ModeracionComentario):
    validate_comment_id(comentarioId)
    try:
        result = comment_service().moderate(
            comentarioId, command.estado, command.moderador_id, command.motivo
        )
        COMMENT_OPERATIONS.labels("moderate", "OK").inc()
        return result
    except DomainError:
        COMMENT_OPERATIONS.labels("moderate", "ERROR").inc()
        raise


@app.post(
    "/api/v1/partidos/{partidoId}/telemetria/posiciones",
    response_model=TelemetryWriteResponse,
    status_code=202,
    responses={
        404: {"description": "Partido inexistente"},
        422: {"description": "Referencia o muestra inválida"},
        503: {"description": "MongoDB o InfluxDB no disponible"},
    },
)
def write_positions(partidoId: str, command: PosicionesBatch):
    validate_match_id(partidoId)
    try:
        repository().validate_position_references(partidoId, command.muestras)
        result = telemetry_service().write_positions(partidoId, command.muestras)
        TELEMETRY_OPERATIONS.labels("write_positions", "OK").inc()
        return result
    except DomainError:
        TELEMETRY_OPERATIONS.labels("write_positions", "ERROR").inc()
        raise


@app.post(
    "/api/v1/partidos/{partidoId}/telemetria/pelota",
    response_model=TelemetryWriteResponse,
    status_code=202,
)
def write_ball_positions(partidoId: str, command: PelotaBatch):
    validate_match_id(partidoId)
    repository().validate_match_teams(
        partidoId,
        [sample.equipo_posesion_id for sample in command.muestras if sample.equipo_posesion_id],
    )
    return telemetry_service().write_ball_positions(partidoId, command.muestras)


@app.get(
    "/api/v1/partidos/{partidoId}/telemetria/pelota",
    response_model=PaginaPelota,
)
def list_ball_positions(
    partidoId: str,
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    limite: int = Query(250, ge=1, le=1000),
):
    validate_match_id(partidoId)
    return telemetry_service().list_ball_positions(partidoId, desde, hasta, limite)


@app.get(
    "/api/v1/partidos/{partidoId}/telemetria/posiciones",
    response_model=PaginaPosiciones,
    responses={
        400: {"description": "Identificador, fecha o cursor inválido"},
        503: {"description": "InfluxDB no disponible"},
    },
)
def list_positions(
    partidoId: str,
    jugador_id: str | None = Query(None, alias="jugadorId", pattern=r"^JUG-[0-9]{4}$"),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
    cursor: str | None = Query(None, min_length=8, max_length=512),
    limite: int = Query(100, ge=1, le=250),
):
    validate_match_id(partidoId)
    try:
        result = telemetry_service().list_positions(
            partidoId, jugador_id, desde, hasta, cursor, limite
        )
        TELEMETRY_OPERATIONS.labels("read_positions", "OK").inc()
        return result
    except DomainError:
        TELEMETRY_OPERATIONS.labels("read_positions", "ERROR").inc()
        raise


@app.get(
    "/api/v1/partidos/{partidoId}/jugadores/{jugadorId}/mapa-calor",
    response_model=MapaCalorResponse,
    responses={
        400: {"description": "Identificador o fecha inválida"},
        413: {"description": "Ventana temporal demasiado amplia"},
        503: {"description": "InfluxDB no disponible"},
    },
)
def get_heatmap(
    partidoId: str,
    jugadorId: str,
    resolucion: int = Query(10, ge=5, le=25),
    desde: datetime | None = Query(None),
    hasta: datetime | None = Query(None),
):
    validate_match_id(partidoId)
    validate_player_id(jugadorId)
    try:
        result = telemetry_service().heatmap(
            partidoId, jugadorId, resolucion, desde, hasta
        )
        TELEMETRY_OPERATIONS.labels("heatmap", "OK").inc()
        return result
    except DomainError:
        TELEMETRY_OPERATIONS.labels("heatmap", "ERROR").inc()
        raise


@app.post(
    "/api/v1/partidos/{partidoId}/telemetria/estadisticas-equipos",
    response_model=TelemetryWriteResponse,
    status_code=202,
    responses={
        404: {"description": "Partido inexistente"},
        422: {"description": "Equipo o muestra inválida"},
        503: {"description": "MongoDB o InfluxDB no disponible"},
    },
)
def write_team_statistics(partidoId: str, command: EstadisticasEquipoBatch):
    validate_match_id(partidoId)
    try:
        repository().validate_match_teams(
            partidoId, [sample.equipo_id for sample in command.muestras]
        )
        result = telemetry_service().write_team_statistics(
            partidoId, command.muestras
        )
        TELEMETRY_OPERATIONS.labels("write_team_statistics", "OK").inc()
        return result
    except DomainError:
        TELEMETRY_OPERATIONS.labels("write_team_statistics", "ERROR").inc()
        raise


@app.post(
    "/api/v1/partidos/{partidoId}/telemetria/agregaciones/15m",
    response_model=AgregacionResponse,
    responses={503: {"description": "InfluxDB no disponible"}},
)
def aggregate_team_statistics(partidoId: str):
    validate_match_id(partidoId)
    try:
        result = telemetry_service().aggregate_team_statistics(partidoId)
        TELEMETRY_OPERATIONS.labels("aggregate_15m", "OK").inc()
        return result
    except DomainError:
        TELEMETRY_OPERATIONS.labels("aggregate_15m", "ERROR").inc()
        raise


@app.get(
    "/api/v1/partidos/{partidoId}/telemetria/resumenes-equipos/15m",
    response_model=PaginaResumenesEquipo,
    responses={503: {"description": "InfluxDB no disponible"}},
)
def list_team_summaries(partidoId: str):
    validate_match_id(partidoId)
    try:
        result = telemetry_service().list_historical_summaries(partidoId)
        TELEMETRY_OPERATIONS.labels("read_summaries", "OK").inc()
        return result
    except DomainError:
        TELEMETRY_OPERATIONS.labels("read_summaries", "ERROR").inc()
        raise


@app.get(
    "/api/v1/grafo/resumen",
    response_model=GrafoResumen,
    responses={503: {"description": "Neo4j no disponible"}},
)
def get_graph_summary():
    try:
        result = graph_service().summary()
        GRAPH_OPERATIONS.labels("summary", "OK").inc()
        return result
    except DomainError:
        GRAPH_OPERATIONS.labels("summary", "ERROR").inc()
        raise


@app.get(
    "/api/v1/grafo/equipos/{equipoId}/rivales",
    response_model=RivalesResponse,
    responses={
        400: {"description": "Identificador inválido"},
        404: {"description": "Equipo inexistente"},
        503: {"description": "Neo4j no disponible"},
    },
)
def get_team_rivals(equipoId: str):
    validate_team_id(equipoId)
    try:
        result = graph_service().rivals(equipoId)
        GRAPH_OPERATIONS.labels("rivals", "OK").inc()
        return result
    except DomainError:
        GRAPH_OPERATIONS.labels("rivals", "ERROR").inc()
        raise


@app.get(
    "/api/v1/grafo/jugadores/{jugadorId}/recomendaciones",
    response_model=RecomendacionesJugadoresResponse,
    responses={
        400: {"description": "Identificador inválido"},
        404: {"description": "Jugador inexistente"},
        503: {"description": "Neo4j no disponible"},
    },
)
def get_player_recommendations(
    jugadorId: str,
    limite: int = Query(10, ge=1, le=50),
):
    validate_player_id(jugadorId)
    try:
        result = graph_service().recommendations(jugadorId, limite)
        GRAPH_OPERATIONS.labels("recommendations", "OK").inc()
        return result
    except DomainError:
        GRAPH_OPERATIONS.labels("recommendations", "ERROR").inc()
        raise


@app.get(
    "/api/v1/grafo/equipos/{origenId}/camino/{destinoId}",
    response_model=CaminoGrafoResponse,
    responses={
        400: {"description": "Identificador inválido"},
        404: {"description": "Equipo o camino inexistente"},
        503: {"description": "Neo4j no disponible"},
    },
)
def get_team_path(origenId: str, destinoId: str):
    validate_team_id(origenId)
    validate_team_id(destinoId)
    try:
        result = graph_service().team_path(origenId, destinoId)
        GRAPH_OPERATIONS.labels("team_path", "OK").inc()
        return result
    except DomainError:
        GRAPH_OPERATIONS.labels("team_path", "ERROR").inc()
        raise


@app.post(
    "/api/v1/analitica/datamart/refrescar",
    response_model=DataMartRefreshResponse,
    responses={503: {"description": "MongoDB, InfluxDB o Data Mart no disponible"}},
)
def refresh_datamart():
    try:
        snapshot = repository().datamart_snapshot()
        summaries = []
        for match in snapshot["partidos"]:
            summaries.extend(
                telemetry_service().list_historical_summaries(match["partidoId"])["items"]
            )
        result = datamart_service().refresh(snapshot, summaries)
        DATAMART_OPERATIONS.labels("refresh", "OK").inc()
        return result
    except DomainError:
        DATAMART_OPERATIONS.labels("refresh", "ERROR").inc()
        raise


@app.get(
    "/api/v1/analitica/datamart/resumen",
    response_model=DataMartSummary,
    responses={503: {"description": "Data Mart no disponible"}},
)
def get_datamart_summary():
    try:
        result = datamart_service().summary()
        DATAMART_OPERATIONS.labels("summary", "OK").inc()
        return result
    except DomainError:
        DATAMART_OPERATIONS.labels("summary", "ERROR").inc()
        raise


@app.get(
    "/api/v1/analitica/datamart/goles-por-equipo",
    response_model=GoalsByTeamResponse,
    responses={503: {"description": "Data Mart no disponible"}},
)
def get_datamart_goals_by_team():
    try:
        result = datamart_service().goals_by_team()
        DATAMART_OPERATIONS.labels("goals_by_team", "OK").inc()
        return result
    except DomainError:
        DATAMART_OPERATIONS.labels("goals_by_team", "ERROR").inc()
        raise


@app.get(
    "/api/v1/analitica/operacional/goles-por-equipo",
    response_model=GoalsByTeamResponse,
    responses={503: {"description": "MongoDB no disponible"}},
)
def get_operational_goals_by_team():
    return repository().operational_goals_by_team()
