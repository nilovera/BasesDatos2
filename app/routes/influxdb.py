from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query, Request

from app.schemas.influxdb import (
    EstadisticasPartidoResponse,
)
from app.services.influxdb import InfluxDBService


router = APIRouter(
    prefix="/api/v1",
    tags=["Estadísticas - InfluxDB"],
)


@router.get(
    "/partidos/{codigo}/estadisticas",
    response_model=EstadisticasPartidoResponse,
    summary="Consultar estadísticas temporales",
    description=(
        "Consulta datos detallados cada 10 segundos "
        "o resúmenes históricos de 15 minutos."
    ),
)
def get_estadisticas(
    request: Request,
    codigo: Annotated[
        str,
        Path(pattern=r"^PAR-\d{4}$"),
    ],
    desde: Annotated[
        datetime,
        Query(),
    ],
    hasta: Annotated[
        datetime,
        Query(),
    ],
    granularidad: Annotated[
        Literal["detalle", "15m"],
        Query(),
    ] = "detalle",
    equipo_id: Annotated[
        str | None,
        Query(pattern=r"^[A-Z]{3}$"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=500),
    ] = 100,
) -> EstadisticasPartidoResponse:
    request.state.dependency = "InfluxDB"

    service = InfluxDBService(
        request.app.state.influxdb_adapter
    )

    return service.get_estadisticas(
        partido_codigo=codigo,
        equipo_id=equipo_id,
        desde=desde,
        hasta=hasta,
        granularidad=granularidad,
        limit=limit,
    )