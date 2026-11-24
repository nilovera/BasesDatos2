import re
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Header, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from .cassandra_client import close_cassandra_client, get_cassandra_session
from .cassandra_service import CassandraCommentService
from .config import settings
from .database import close_client, get_client
from .errors import DomainError
from .metrics import (
    CACHE_INVALIDATIONS,
    CACHE_READS,
    COMMENT_OPERATIONS,
    DEPENDENCY_UP,
    EVENTS_CONFIRMED,
    HTTP_DURATION,
    HTTP_REQUESTS,
    IDEMPOTENCY_REPLAYS,
    OUTBOX_PENDING,
    SESSION_OPERATIONS,
)
from .models import (
    EventoCommand,
    EventoConfirmado,
    ComentarioCreate,
    ComentarioCreado,
    HealthResponse,
    ModeracionComentario,
    ModeracionResponse,
    PaginaComentarios,
    PaginaEventos,
    PartidoResponse,
    SesionCreate,
    SesionRenovacion,
    SesionResponse,
)
from .redis_client import RedisError, close_redis_client, get_redis_client
from .redis_service import RedisService
from .repository import MongoRepository


PARTIDO_ID = re.compile(r"^PAR-[0-9]{4}$")
USER_ID = re.compile(r"^USR-[0-9]{4}$")
COMMENT_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
SESSION_ID = re.compile(
    r"^SES-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


@asynccontextmanager
async def lifespan(_app):
    try:
        OUTBOX_PENDING.set(MongoRepository(get_client()).pending_outbox())
    except Exception:
        # El healthcheck informará la indisponibilidad sin impedir que el
        # proceso arranque y exponga diagnóstico.
        pass
    yield
    close_cassandra_client()
    close_redis_client()
    close_client()


app = FastAPI(
    title="Fixture 2030 API",
    version="0.4.0",
    description="Núcleo deportivo en MongoDB, cache y sesiones en Redis, y comentarios en Cassandra.",
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


def request_id(request):
    return getattr(request.state, "request_id", str(uuid4()))


def validate_match_id(partido_id):
    if not PARTIDO_ID.fullmatch(partido_id):
        raise DomainError(400, "INVALID_MATCH_ID", "Formato de partidoId inválido")


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
    DEPENDENCY_UP.labels("mongodb").set(1 if mongo_status == "PRIMARY" else 0)
    DEPENDENCY_UP.labels("redis").set(1 if redis_status == "UP" else 0)
    DEPENDENCY_UP.labels("cassandra").set(1 if cassandra_status == "UP" else 0)
    return {
        "service": "fixture2030-api",
        "status": "UP"
        if mongo_status == "PRIMARY" and redis_status == "UP" and cassandra_status == "UP"
        else "DEGRADED",
        "mongodb": mongo_status,
        "redis": redis_status,
        "cassandra": cassandra_status,
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
    try:
        OUTBOX_PENDING.set(repository().pending_outbox())
    except Exception:
        pass
    invalidated = redis_service().invalidate_match(partidoId)
    CACHE_INVALIDATIONS.labels("DELETED" if invalidated else "ABSENT_OR_UNAVAILABLE").inc()
    return result.body


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
