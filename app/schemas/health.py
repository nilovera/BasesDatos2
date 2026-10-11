from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    estado: Literal["ok"]
    servicio: str
    version: str
    entorno: str