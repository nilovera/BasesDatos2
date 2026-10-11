from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class ComentarioResponse(BaseModel):
    comentario_id: UUID
    creado_en: datetime
    usuario_id: str
    usuario_nombre: str
    contenido: str
    likes: int
    estado_moderacion: str


class PaginacionCassandra(BaseModel):
    limite: int
    siguiente_page_state: str | None
    hay_mas: bool


class ComentariosPartidoResponse(BaseModel):
    partido_codigo: str
    bucket_10min: str
    datos: list[ComentarioResponse]
    paginacion: PaginacionCassandra
    fuente_datos: Literal["Cassandra"] = "Cassandra"