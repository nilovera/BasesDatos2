from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.schemas.redis import (
    CierreSesionResponse,
    SesionResponse,
)
from app.services.redis import RedisService


router = APIRouter(
    prefix="/api/v1",
    tags=["Sesiones - Redis"],
)


SesionId = Annotated[
    str,
    Path(
        min_length=8,
        max_length=40,
        pattern=(
            r"^SES-[A-Z0-9]+"
            r"(?:-[A-Z0-9]+)*$"
        ),
    ),
]


@router.get(
    "/sesiones/{sesion_id}",
    response_model=SesionResponse,
    summary="Consultar una sesión vigente",
)
def get_sesion(
    request: Request,
    sesion_id: SesionId,
) -> SesionResponse:
    request.state.dependency = "Redis"

    service = RedisService(
        request.app.state.redis_adapter
    )
    return service.get_sesion(sesion_id)


@router.delete(
    "/sesiones/{sesion_id}",
    response_model=CierreSesionResponse,
    summary="Cerrar una sesión",
)
def cerrar_sesion(
    request: Request,
    sesion_id: SesionId,
) -> CierreSesionResponse:
    request.state.dependency = "Redis"

    service = RedisService(
        request.app.state.redis_adapter
    )
    return service.cerrar_sesion(sesion_id)