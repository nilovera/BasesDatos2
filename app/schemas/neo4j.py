from datetime import date
from typing import Literal

from pydantic import BaseModel


class EquipoGrafoResponse(BaseModel):
    codigo: str
    nombre: str
    confederacion: str


class SedeGrafoResponse(BaseModel):
    codigo: str
    nombre: str


class EventoGrafoResponse(BaseModel):
    codigo: str
    tipo: str
    minuto: int


class PartidoEventosResponse(BaseModel):
    codigo: str
    fecha: date
    fase: str
    equipos: list[EquipoGrafoResponse]
    sede: SedeGrafoResponse | None
    eventos: list[EventoGrafoResponse]
    fuente_datos: Literal["Neo4j"] = "Neo4j"