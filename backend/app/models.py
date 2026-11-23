from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class EventTimestamp(ApiModel):
    ocurrido_en: datetime = Field(alias="ocurridoEn")

    @field_validator("ocurrido_en")
    @classmethod
    def timestamp_must_have_timezone(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("ocurridoEn debe incluir zona horaria")
        return value


class InicioPartidoCommand(EventTimestamp):
    tipo: Literal["INICIO_PARTIDO"]


class GolFields(ApiModel):
    tipo: Literal["GOL"]
    periodo: int = Field(ge=1, le=5)
    minuto: int = Field(ge=0, le=150)
    equipo_id: str = Field(alias="equipoId", pattern=r"^EQ-[0-9]{2}$")
    jugador_id: str = Field(alias="jugadorId", pattern=r"^JUG-[0-9]{4}$")


class GolCommand(EventTimestamp, GolFields):
    pass


class SustitucionFields(ApiModel):
    tipo: Literal["SUSTITUCION"]
    periodo: int = Field(ge=1, le=5)
    minuto: int = Field(ge=0, le=150)
    equipo_id: str = Field(alias="equipoId", pattern=r"^EQ-[0-9]{2}$")
    sale_jugador_id: str = Field(
        alias="saleJugadorId", pattern=r"^JUG-[0-9]{4}$"
    )
    entra_jugador_id: str = Field(
        alias="entraJugadorId", pattern=r"^JUG-[0-9]{4}$"
    )


class SustitucionCommand(EventTimestamp, SustitucionFields):
    pass


Replacement = Annotated[
    Union[GolFields, SustitucionFields], Field(discriminator="tipo")
]


class CorreccionEventoCommand(EventTimestamp):
    tipo: Literal["CORRECCION_EVENTO"]
    evento_original_id: str = Field(
        alias="eventoOriginalId", pattern=r"^EVE-[0-9]{6}$"
    )
    motivo: str = Field(min_length=3, max_length=300)
    reemplazo: Replacement


EventoCommand = Annotated[
    Union[
        InicioPartidoCommand,
        GolCommand,
        SustitucionCommand,
        CorreccionEventoCommand,
    ],
    Field(discriminator="tipo"),
]


class Marcador(ApiModel):
    local: int = Field(ge=0)
    visitante: int = Field(ge=0)


class PartidoResponse(ApiModel):
    partido_id: str = Field(alias="partidoId")
    local_id: str = Field(alias="localId")
    visitante_id: str = Field(alias="visitanteId")
    inicio_programado: datetime = Field(alias="inicioProgramado")
    estado: str
    marcador: Marcador
    version: int


class EventoConfirmado(ApiModel):
    evento_id: str = Field(alias="eventoId")
    partido_id: str = Field(alias="partidoId")
    secuencia: int
    tipo: str
    estado_partido: str = Field(alias="estadoPartido")
    marcador: Marcador
    version_partido: int = Field(alias="versionPartido")
    propagacion: Literal["PENDIENTE", "PUBLICADA"]


class EventoResumen(ApiModel):
    evento_id: str = Field(alias="eventoId")
    secuencia: int
    tipo: str
    ocurrido_en: datetime = Field(alias="ocurridoEn")


class PaginaEventos(ApiModel):
    items: list[EventoResumen]
    siguiente_secuencia: int | None = Field(alias="siguienteSecuencia")


class HealthResponse(ApiModel):
    status: Literal["UP", "DEGRADED"]
    service: Literal["fixture2030-api"]
    mongodb: str
