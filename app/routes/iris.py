from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.schemas.iris import PartidoIRISResponse
from app.services.iris import IRISService


router = APIRouter(
    prefix="/api/v1",
    tags=["Persistencia de objetos - IRIS"],
)


@router.get(
    "/partidos/{codigo}/detalle",
    response_model=PartidoIRISResponse,
    summary="Consultar un partido persistente",
    description=(
        "Recupera desde IRIS el partido, "
        "su árbitro principal y sus eventos."
    ),
)
def get_partido_detalle(
    request: Request,
    codigo: Annotated[
        str,
        Path(pattern=r"^PAR-[A-Z0-9]{4,12}$"),
    ],
) -> PartidoIRISResponse:
    request.state.dependency = "InterSystems IRIS"

    service = IRISService(
        request.app.state.iris_adapter
    )

    return service.get_partido_detalle(codigo)