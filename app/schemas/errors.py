from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    codigo: str
    mensaje: str
    request_id: str
    detalles: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail