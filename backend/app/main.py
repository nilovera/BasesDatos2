import re
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Header, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from .database import close_client, get_client
from .errors import DomainError
from .metrics import (
    EVENTS_CONFIRMED,
    HTTP_DURATION,
    HTTP_REQUESTS,
    IDEMPOTENCY_REPLAYS,
    OUTBOX_PENDING,
)
from .models import (
    EventoCommand,
    EventoConfirmado,
    HealthResponse,
    PaginaEventos,
    PartidoResponse,
)
from .repository import MongoRepository


PARTIDO_ID = re.compile(r"^PAR-[0-9]{4}$")


@asynccontextmanager
async def lifespan(_app):
    try:
        OUTBOX_PENDING.set(MongoRepository(get_client()).pending_outbox())
    except Exception:
        # El healthcheck informará la indisponibilidad sin impedir que el
        # proceso arranque y exponga diagnóstico.
        pass
    yield
    close_client()


app = FastAPI(
    title="Fixture 2030 API",
    version="0.2.0",
    description="Núcleo deportivo autoritativo en MongoDB.",
    lifespan=lifespan,
)
app.mount("/metrics", make_asgi_app())


def repository():
    return MongoRepository(get_client())


def request_id(request):
    return getattr(request.state, "request_id", str(uuid4()))


def validate_match_id(partido_id):
    if not PARTIDO_ID.fullmatch(partido_id):
        raise DomainError(400, "INVALID_MATCH_ID", "Formato de partidoId inválido")


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
    return repository().health()


@app.get("/api/v1/partidos/{partidoId}", response_model=PartidoResponse)
def get_match(partidoId: str):
    validate_match_id(partidoId)
    return repository().get_match(partidoId)


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
    responses={200: {"model": EventoConfirmado}},
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
    return result.body
