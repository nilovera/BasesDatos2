from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, field_validator


class PuntoTemporalUTC(BaseModel):
    time: datetime

    @field_validator("time")
    @classmethod
    def normalizar_utc(
        cls,
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(timezone.utc)


class PuntoDetalleResponse(PuntoTemporalUTC):
    equipo_id: str
    posesion_pct: float
    pases_intervalo: int
    tiros_acumulados: int


class Resumen15MinutosResponse(PuntoTemporalUTC):
    equipo_id: str
    posesion_promedio: float
    pases_total: int
    muestras: int


class MetadataEstadisticas(BaseModel):
    limite: int
    cantidad: int
    hay_mas: bool
    desde: datetime
    hasta: datetime
    intervalo_fuente: str


class EstadisticasPartidoResponse(BaseModel):
    partido_codigo: str
    granularidad: Literal["detalle", "15m"]
    equipo_id: str | None
    datos: list[
        PuntoDetalleResponse
        | Resumen15MinutosResponse
    ]
    metadata: MetadataEstadisticas
    fuente_datos: Literal["InfluxDB"] = "InfluxDB"