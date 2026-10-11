from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Request,
)

from app.adapters.neo4j import Neo4jAdapter
from app.schemas.errors import ErrorResponse
from app.schemas.neo4j import PartidoEventosResponse
from app.services.neo4j import Neo4jService


router = APIRouter(
    prefix="/api/v1",
    tags=["Neo4j"],
)


def get_neo4j_service(
    request: Request,
) -> Neo4jService:
    request.state.dependency = "Neo4j"

    adapter: Neo4jAdapter = (
        request.app.state.neo4j_adapter
    )

    return Neo4jService(adapter)


@router.get(
    "/partidos/{codigo}/eventos",
    response_model=PartidoEventosResponse,
    summary=(
        "Obtener contexto y eventos de un partido"
    ),
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def get_partido_eventos(
    codigo: Annotated[
        str,
        Path(
            pattern=r"^PAR-\d{4}$",
            description="Código del partido.",
            examples=["PAR-0001"],
        ),
    ],
    service: Neo4jService = Depends(
        get_neo4j_service
    ),
) -> PartidoEventosResponse:
    return service.get_partido_eventos(codigo)