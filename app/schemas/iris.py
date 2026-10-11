from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ArbitroIRISResponse(BaseModel):
    id: int
    documento: str
    nombre: str
    nacionalidad: str
    rol: str
    licencia_fifa: bool


class EventoIRISResponse(BaseModel):
    id: str
    tipo: str
    minuto: int
    detalle: str


class PartidoIRISResponse(BaseModel):
    id: int
    codigo: str
    fecha_hora: datetime
    equipo_local_id: str
    equipo_visitante_id: str
    estado: str
    arbitro_principal: ArbitroIRISResponse | None
    eventos: list[EventoIRISResponse]
    fuente_datos: Literal[
        "InterSystems IRIS"
    ] = "InterSystems IRIS"