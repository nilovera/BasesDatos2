from typing import Annotated

from fastapi import APIRouter, Path, Query, Request

from app.services.cassandra import CassandraService
from app.schemas.cassandra import (
    ComentariosPartidoResponse,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Comentarios - Cassandra"],
)


@router.get(
    "/partidos/{codigo}/comentarios",
    response_model=ComentariosPartidoResponse,
    summary="Listar comentarios de un partido",
    description=(
        "Consulta Cassandra utilizando la partición "
        "(partido_id, bucket_10min) y paginación nativa."
    ),
)
def get_comentarios_por_partido(
    request: Request,
    codigo: Annotated[
        str,
        Path(pattern=r"^PAR-\d{4}$"),
    ],
    bucket_10min: Annotated[
        str,
        Query(
            pattern=(
                r"^\d{10}"
                r"(00|10|20|30|40|50)$"
            )
        ),
    ],
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 10,
    page_state: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=4096,
            pattern=r"^[A-Za-z0-9_-]+$",
        ),
    ] = None,
) -> ComentariosPartidoResponse:
    request.state.dependency = "Cassandra"

    service = CassandraService(
        request.app.state.cassandra_adapter
    )

    return service.get_comentarios_por_partido(
        partido_codigo=codigo,
        bucket_10min=bucket_10min,
        limit=limit,
        page_state=page_state,
    )