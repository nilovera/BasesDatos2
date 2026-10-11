import base64
import binascii
from typing import Any

from cassandra import InvalidRequest, OperationTimedOut, ReadTimeout
from cassandra.cluster import Cluster, NoHostAvailable

from app.config.settings import Settings
from app.exceptions import (
    ApiError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


class CassandraAdapter:
    def __init__(self, settings: Settings) -> None:
        self._timeout = settings.dependency_timeout_seconds

        self._cluster = Cluster(
            contact_points=settings.cassandra_contact_points,
            port=settings.cassandra_port,
            connect_timeout=self._timeout,
        )

        self._session = self._cluster.connect(
            settings.cassandra_keyspace
        )
        self._session.default_timeout = self._timeout

        self._comentarios_por_partido = (
            self._session.prepare(
                """
                SELECT
                    partido_id,
                    bucket_10min,
                    creado_en,
                    comentario_id,
                    contenido,
                    estado_moderacion,
                    likes,
                    usuario_id,
                    usuario_nombre
                FROM comentarios_por_partido
                WHERE partido_id = ?
                  AND bucket_10min = ?
                """
            )
        )

    def close(self) -> None:
        self._session.shutdown()
        self._cluster.shutdown()

    def get_comentarios_por_partido(
        self,
        partido_codigo: str,
        bucket_10min: str,
        limit: int,
        page_state: str | None,
    ) -> dict[str, Any]:
        paging_state = self._decode_page_state(page_state)

        statement = self._comentarios_por_partido.bind(
            (partido_codigo, bucket_10min)
        )
        statement.fetch_size = limit

        try:
            result = self._session.execute(
                statement,
                timeout=self._timeout,
                paging_state=paging_state,
            )
        except (OperationTimedOut, ReadTimeout) as error:
            raise DependencyTimeoutError(
                "Cassandra"
            ) from error
        except NoHostAvailable as error:
            raise DependencyUnavailableError(
                "Cassandra"
            ) from error
        except InvalidRequest as error:
            if page_state is not None:
                raise ApiError(
                    status_code=422,
                    code="PAGINACION_INVALIDA",
                    message=(
                        "El page_state recibido no es vÃ¡lido "
                        "para esta consulta."
                    ),
                ) from error
            raise

        rows = [
            {
                "comentario_id": row.comentario_id,
                "creado_en": row.creado_en,
                "usuario_id": row.usuario_id,
                "usuario_nombre": row.usuario_nombre,
                "contenido": row.contenido,
                "likes": row.likes,
                "estado_moderacion": (
                    row.estado_moderacion
                ),
            }
            for row in result.current_rows
        ]

        next_page_state = None

        if result.paging_state is not None:
            next_page_state = (
                base64.urlsafe_b64encode(
                    result.paging_state
                )
                .decode("ascii")
                .rstrip("=")
            )

        return {
            "rows": rows,
            "next_page_state": next_page_state,
            "has_more": bool(result.has_more_pages),
        }

    @staticmethod
    def _decode_page_state(
        page_state: str | None,
    ) -> bytes | None:
        if page_state is None:
            return None

        try:
            padding = "=" * (-len(page_state) % 4)
            return base64.b64decode(
                page_state + padding,
                altchars=b"-_",
                validate=True,
            )
        except (ValueError, binascii.Error) as error:
            raise ApiError(
                status_code=422,
                code="PAGINACION_INVALIDA",
                message=(
                    "El page_state recibido no tiene "
                    "un formato vÃ¡lido."
                ),
            ) from error