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
    redis: str
    cassandra: str


class SesionCreate(ApiModel):
    usuario_id: str = Field(alias="usuarioId", pattern=r"^USR-[0-9]{4}$")
    rol: Literal["FAN", "OPERADOR", "ADMIN"] = "FAN"
    ttl_segundos: int = Field(alias="ttlSegundos", ge=60, le=3600, default=1800)


class SesionRenovacion(ApiModel):
    ttl_segundos: int = Field(alias="ttlSegundos", ge=60, le=3600)


class SesionResponse(ApiModel):
    sesion_id: str = Field(alias="sesionId")
    usuario_id: str = Field(alias="usuarioId")
    rol: str
    creada_en: datetime = Field(alias="creadaEn")
    ultimo_acceso: datetime = Field(alias="ultimoAcceso")
    renovaciones: int = Field(ge=0)
    ttl_segundos: int = Field(alias="ttlSegundos", ge=0)


class ComentarioCreate(ApiModel):
    usuario_id: str = Field(alias="usuarioId", pattern=r"^USR-[0-9]{4}$")
    contenido: str = Field(min_length=1, max_length=280)


class ComentarioResponse(ApiModel):
    comentario_id: str = Field(alias="comentarioId")
    partido_id: str = Field(alias="partidoId")
    usuario_id: str = Field(alias="usuarioId")
    contenido: str | None
    estado: Literal["VISIBLE", "OCULTO"]
    creado_en: datetime = Field(alias="creadoEn")


class ComentarioCreado(ComentarioResponse):
    bucket: str = Field(pattern=r"^[0-9]{12}$")
    shard: int = Field(ge=0, le=15)
    repetido: bool


class PaginaComentarios(ApiModel):
    items: list[ComentarioResponse]
    siguiente_cursor: datetime | None = Field(alias="siguienteCursor")


class ModeracionComentario(ApiModel):
    estado: Literal["VISIBLE", "OCULTO"]
    moderador_id: str = Field(alias="moderadorId", pattern=r"^USR-[0-9]{4}$")
    motivo: str = Field(min_length=3, max_length=300)


class ModeracionResponse(ApiModel):
    comentario_id: str = Field(alias="comentarioId")
    estado: Literal["VISIBLE", "OCULTO"]
    moderado_en: datetime = Field(alias="moderadoEn")
    moderador_id: str = Field(alias="moderadorId")
    motivo: str
