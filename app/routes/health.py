from fastapi import APIRouter, Depends

from app.config.settings import Settings, get_settings
from app.schemas.health import HealthResponse


router = APIRouter(tags=["Sistema"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Comprobar disponibilidad de la API",
)
def health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    return HealthResponse(
        estado="ok",
        servicio=settings.app_name,
        version=settings.app_version,
        entorno=settings.app_env,
    )