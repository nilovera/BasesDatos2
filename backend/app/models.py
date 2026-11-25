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
    influxdb: str
    neo4j: str


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
    siguiente_cursor: str | None = Field(
        alias="siguienteCursor",
        description="Cursor opaco para solicitar la página siguiente",
    )


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


class TelemetryTimestamp(ApiModel):
    capturado_en: datetime = Field(alias="capturadoEn")

    @field_validator("capturado_en")
    @classmethod
    def timestamp_must_have_timezone(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("capturadoEn debe incluir zona horaria")
        return value


class PosicionMuestra(TelemetryTimestamp):
    equipo_id: str = Field(alias="equipoId", pattern=r"^EQ-[0-9]{2}$")
    jugador_id: str = Field(alias="jugadorId", pattern=r"^JUG-[0-9]{4}$")
    x: float = Field(ge=0, le=100, allow_inf_nan=False)
    y: float = Field(ge=0, le=100, allow_inf_nan=False)
    periodo: int = Field(ge=1, le=5)
    segundo_partido: int = Field(alias="segundoPartido", ge=0, le=10800)


class PosicionesBatch(ApiModel):
    muestras: list[PosicionMuestra] = Field(min_length=1, max_length=250)


class EstadisticaEquipoMuestra(TelemetryTimestamp):
    equipo_id: str = Field(alias="equipoId", pattern=r"^EQ-[0-9]{2}$")
    posesion_pct: float = Field(alias="posesionPct", ge=0, le=100, allow_inf_nan=False)
    pases_intervalo: int = Field(alias="pasesIntervalo", ge=0, le=1000)
    tiros_acumulados: int = Field(alias="tirosAcumulados", ge=0, le=1000)
    goles_acumulados: int = Field(alias="golesAcumulados", ge=0, le=100)
    periodo: int = Field(ge=1, le=5)
    segundo_partido: int = Field(alias="segundoPartido", ge=0, le=10800)


class EstadisticasEquipoBatch(ApiModel):
    muestras: list[EstadisticaEquipoMuestra] = Field(min_length=1, max_length=250)


class TelemetryWriteResponse(ApiModel):
    partido_id: str = Field(alias="partidoId")
    muestras_aceptadas: int = Field(alias="muestrasAceptadas", ge=1)
    repetible: bool
    base: str


class PosicionResponse(PosicionMuestra):
    partido_id: str = Field(alias="partidoId")


class PaginaPosiciones(ApiModel):
    items: list[PosicionResponse]
    siguiente_cursor: str | None = Field(
        alias="siguienteCursor",
        description="Cursor opaco (timestamp, jugadorId) para continuar sin omisiones",
    )


class CeldaMapaCalor(ApiModel):
    celda_x: int = Field(alias="celdaX", ge=0)
    celda_y: int = Field(alias="celdaY", ge=0)
    x_desde: float = Field(alias="xDesde", ge=0, le=100)
    x_hasta: float = Field(alias="xHasta", ge=0, le=100)
    y_desde: float = Field(alias="yDesde", ge=0, le=100)
    y_hasta: float = Field(alias="yHasta", ge=0, le=100)
    muestras: int = Field(ge=1)


class MapaCalorResponse(ApiModel):
    partido_id: str = Field(alias="partidoId")
    jugador_id: str = Field(alias="jugadorId")
    resolucion: int = Field(ge=5, le=25)
    total_muestras: int = Field(alias="totalMuestras", ge=0)
    celdas: list[CeldaMapaCalor]


class AgregacionResponse(ApiModel):
    partido_id: str = Field(alias="partidoId")
    resumenes_generados: int = Field(alias="resumenesGenerados", ge=0)
    ventana_minutos: Literal[15] = Field(alias="ventanaMinutos", default=15)
    base_destino: str = Field(alias="baseDestino")


class ResumenEquipoHistorico(ApiModel):
    partido_id: str = Field(alias="partidoId")
    equipo_id: str = Field(alias="equipoId")
    ventana_inicio: datetime = Field(alias="ventanaInicio")
    posesion_promedio: float = Field(alias="posesionPromedio", ge=0, le=100)
    pases_total: int = Field(alias="pasesTotal", ge=0)
    tiros_finales: int = Field(alias="tirosFinales", ge=0)
    goles_finales: int = Field(alias="golesFinales", ge=0)
    muestras: int = Field(ge=1)


class PaginaResumenesEquipo(ApiModel):
    items: list[ResumenEquipoHistorico]


class GrafoResumen(ApiModel):
    equipos: int = Field(ge=0)
    jugadores: int = Field(ge=0)
    partidos: int = Field(ge=0)
    confederaciones: int = Field(ge=0)
    relaciones: int = Field(ge=0)


class RivalEquipo(ApiModel):
    partido_id: str = Field(alias="partidoId")
    equipo_id: str = Field(alias="equipoId")
    nombre: str
    inicio_programado: str = Field(alias="inicioProgramado")


class RivalesResponse(ApiModel):
    equipo_id: str = Field(alias="equipoId")
    items: list[RivalEquipo]


class JugadorRecomendado(ApiModel):
    jugador_id: str = Field(alias="jugadorId")
    nombre: str
    posicion: str
    equipo_id: str = Field(alias="equipoId")
    equipo: str
    diferencia_ranking: int = Field(alias="diferenciaRanking", ge=0)
    criterio: str


class RecomendacionesJugadoresResponse(ApiModel):
    jugador_id: str = Field(alias="jugadorId")
    criterio: Literal["MISMA_POSICION_Y_CONFEDERACION"]
    items: list[JugadorRecomendado]


class CaminoGrafoNodo(ApiModel):
    tipo: str
    id: str
    nombre: str


class CaminoGrafoResponse(ApiModel):
    origen_id: str = Field(alias="origenId")
    destino_id: str = Field(alias="destinoId")
    nodos: list[CaminoGrafoNodo]
    relaciones: list[str]
    saltos: int = Field(ge=0, le=4)
