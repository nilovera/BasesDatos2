from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SesionResponse(BaseModel):
    sesion_id: str
    usuario_id: str
    rol: str
    ultimo_acceso: datetime
    estado: str
    partido_actual: str | None
    acciones: int = Field(ge=0)
    ttl_segundos: int = Field(gt=0)
    fuente_datos: Literal["Redis"] = "Redis"


class CierreSesionResponse(BaseModel):
    sesion_id: str
    cerrada: bool
    mensaje: str
    fuente_datos: Literal["Redis"] = "Redis"