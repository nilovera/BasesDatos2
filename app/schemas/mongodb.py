from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class PosicionJugador(str, Enum):
    arquero = "Arquero"
    defensor = "Defensor"
    mediocampista = "Mediocampista"
    delantero = "Delantero"


class EquipoResponse(BaseModel):
    codigo: str
    nombre: str
    confederacion: str
    ranking: int
    fuente_datos: Literal["MongoDB"] = "MongoDB"


class JugadorResponse(BaseModel):
    codigo: str
    nombre: str
    fecha_nacimiento: date
    posicion: PosicionJugador
    equipo_codigo: str


class PaginationMetadata(BaseModel):
    limite: int = Field(ge=1)
    siguiente_cursor: str | None
    hay_mas: bool


class JugadoresPageResponse(BaseModel):
    datos: list[JugadorResponse]
    paginacion: PaginationMetadata
    fuente_datos: Literal["MongoDB"] = "MongoDB"