from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Request,
)

from app.adapters.mongodb import MongoAdapter
from app.schemas.errors import ErrorResponse
from app.schemas.mongodb import (
    EquipoResponse,
    JugadoresPageResponse,
    PosicionJugador,
)
from app.services.mongodb import MongoService


router = APIRouter(
    prefix="/api/v1",
    tags=["MongoDB"],
)


def get_mongo_service(
    request: Request,
) -> MongoService:
    request.state.dependency = "MongoDB"

    adapter: MongoAdapter = (
        request.app.state.mongo_adapter
    )

    return MongoService(adapter)


@router.get(
    "/equipos/{codigo}",
    response_model=EquipoResponse,
    summary="Obtener un equipo por código",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def get_equipo(
    codigo: Annotated[
        str,
        Path(
            pattern=r"^EQ-\d{2}$",
            description="Código del equipo.",
            examples=["EQ-01"],
        ),
    ],
    service: MongoService = Depends(
        get_mongo_service
    ),
) -> EquipoResponse:
    return service.get_equipo(codigo)


@router.get(
    "/jugadores",
    response_model=JugadoresPageResponse,
    summary="Listar jugadores de un equipo",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def list_jugadores(
    equipo_codigo: Annotated[
        str,
        Query(
            pattern=r"^EQ-\d{2}$",
            description="Equipo requerido.",
            examples=["EQ-01"],
        ),
    ],
    posicion: PosicionJugador | None = Query(
        default=None,
        description="Posición deportiva opcional.",
    ),
    cursor: Annotated[
        str | None,
        Query(
            pattern=r"^JUG-\d{4}$",
            description=(
                "Último código recibido en "
                "la página anterior."
            ),
            examples=["JUG-0003"],
        ),
    ] = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Cantidad máxima de resultados.",
        ),
    ] = 20,
    service: MongoService = Depends(
        get_mongo_service
    ),
) -> JugadoresPageResponse:
    return service.list_jugadores(
        equipo_codigo=equipo_codigo,
        posicion=posicion,
        cursor=cursor,
        limit=limit,
    )