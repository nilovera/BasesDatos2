from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from app.config.settings import Settings, get_settings
from app.schemas.health import (
    DependenciasResponse,
    HealthResponse,
    ReadinessResponse,
)
from app.services.dependency_health import readiness_from


router = APIRouter(tags=["Sistema"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Comprobar disponibilidad de la API",
    description=(
        "Se mantiene por compatibilidad con el Hito 10. "
        "Equivale a /health/live: no consulta ninguna base."
    ),
)
@router.get(
    "/health/live",
    response_model=HealthResponse,
    summary="Liveness: el proceso de la API está activo",
    description=(
        "No consulta dependencias. Responde 200 mientras el proceso "
        "pueda atender solicitudes HTTP."
    ),
)
def health(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    request.state.dependency = "api"
    return HealthResponse(
        estado="ok",
        servicio=settings.app_name,
        version=settings.app_version,
        entorno=settings.app_env,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness: la API está preparada para recibir tráfico",
    description=(
        "Usa el último diagnóstico por dependencia (caché de 15 s). "
        "ready=200, degraded=200, not_ready=503."
    ),
    responses={503: {"model": ReadinessResponse}},
)
def readiness(request: Request):
    request.state.dependency = "health"
    snapshot = request.app.state.health_checker.snapshot()
    estado, status_code = readiness_from(snapshot["dependencias"])

    body = ReadinessResponse(
        estado=estado,
        dependencias={
            item["dependencia"]: item["estado"]
            for item in snapshot["dependencias"]
        },
        desde_cache=snapshot["desde_cache"],
        antiguedad_segundos=snapshot["antiguedad_segundos"],
    )

    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
    )


@router.get(
    "/health/dependencias",
    response_model=DependenciasResponse,
    summary="Diagnóstico individual por dependencia",
    description=(
        "Ejecuta (o reutiliza de la caché) el ping liviano de cada "
        "adaptador con timeout propio. No expone mensajes de drivers "
        "ni credenciales."
    ),
)
def dependencias(
    request: Request,
    refrescar: bool = Query(
        default=False,
        description=(
            "Fuerza un nuevo chequeo. Limitado a uno cada 5 segundos."
        ),
    ),
) -> DependenciasResponse:
    request.state.dependency = "health"
    snapshot = request.app.state.health_checker.snapshot(
        refresh=refrescar
    )
    estado, _ = readiness_from(snapshot["dependencias"])

    return DependenciasResponse(estado_general=estado, **snapshot)
