from datetime import datetime

from app.adapters.mongodb import MongoAdapter
from app.exceptions import ResourceNotFoundError
from app.schemas.mongodb import (
    EquipoResponse,
    JugadorResponse,
    JugadoresPageResponse,
    PaginationMetadata,
    PosicionJugador,
)


class MongoService:
    def __init__(self, adapter: MongoAdapter) -> None:
        self._adapter = adapter

    def get_equipo(
        self,
        codigo: str,
    ) -> EquipoResponse:
        document = self._adapter.get_equipo(codigo)

        if document is None:
            raise ResourceNotFoundError(
                resource="el equipo",
                identifier=codigo,
            )

        return EquipoResponse(
            codigo=document["_id"],
            nombre=document["nombre"],
            confederacion=document["confederacion"],
            ranking=int(document["ranking"]),
        )

    def list_jugadores(
        self,
        equipo_codigo: str,
        posicion: PosicionJugador | None,
        cursor: str | None,
        limit: int,
    ) -> JugadoresPageResponse:
        equipo = self._adapter.get_equipo(
            equipo_codigo
        )

        if equipo is None:
            raise ResourceNotFoundError(
                resource="el equipo",
                identifier=equipo_codigo,
            )

        documents, has_more = (
            self._adapter.list_jugadores(
                equipo_codigo=equipo_codigo,
                posicion=(
                    posicion.value
                    if posicion is not None
                    else None
                ),
                cursor=cursor,
                limit=limit,
            )
        )

        jugadores = [
            JugadorResponse(
                codigo=document["_id"],
                nombre=document["nombre"],
                fecha_nacimiento=self._to_date(
                    document["fecha_nacimiento"]
                ),
                posicion=document["posicion"],
                equipo_codigo=document["equipo_id"],
            )
            for document in documents
        ]

        next_cursor = (
            jugadores[-1].codigo
            if has_more and jugadores
            else None
        )

        return JugadoresPageResponse(
            datos=jugadores,
            paginacion=PaginationMetadata(
                limite=limit,
                siguiente_cursor=next_cursor,
                hay_mas=has_more,
            ),
        )

    @staticmethod
    def _to_date(value: datetime):
        return value.date()