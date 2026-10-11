from app.adapters.cassandra import CassandraAdapter
from app.schemas.cassandra import (
    ComentarioResponse,
    ComentariosPartidoResponse,
    PaginacionCassandra,
)


class CassandraService:
    def __init__(
        self,
        adapter: CassandraAdapter,
    ) -> None:
        self._adapter = adapter

    def get_comentarios_por_partido(
        self,
        partido_codigo: str,
        bucket_10min: str,
        limit: int,
        page_state: str | None,
    ) -> ComentariosPartidoResponse:
        result = (
            self._adapter.get_comentarios_por_partido(
                partido_codigo=partido_codigo,
                bucket_10min=bucket_10min,
                limit=limit,
                page_state=page_state,
            )
        )

        return ComentariosPartidoResponse(
            partido_codigo=partido_codigo,
            bucket_10min=bucket_10min,
            datos=[
                ComentarioResponse(**row)
                for row in result["rows"]
            ],
            paginacion=PaginacionCassandra(
                limite=limit,
                siguiente_page_state=(
                    result["next_page_state"]
                ),
                hay_mas=result["has_more"],
            ),
        )