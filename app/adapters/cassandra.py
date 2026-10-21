import base64
import binascii
import logging
import threading
from typing import Any

from cassandra import (
    AuthenticationFailed,
    InvalidRequest,
    OperationTimedOut,
    ReadTimeout,
    Unauthorized,
)
from cassandra.cluster import Cluster, NoHostAvailable

from app.config.settings import Settings
from app.exceptions import (
    ApiError,
    DependencyMisconfiguredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


logger = logging.getLogger("fixture2030.cassandra")


COMENTARIOS_POR_PARTIDO_CQL = """
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


class CassandraAdapter:
    """Adaptador de Cassandra con conexión diferida.

    Hasta el Hito 10 la sesión se abría en el constructor, dentro del
    lifespan de FastAPI. Si Cassandra no estaba disponible al iniciar,
    la API completa no arrancaba y arrastraba a los otros cinco motores.
    Desde el Hito 11 la sesión se abre en la primera solicitud que la
    necesita; si falla, se responde 503/504 y el próximo intento vuelve a
    probar (una sola vez por solicitud, sin reintentos ilimitados).
    """

    dependency_name = "Cassandra"

    def __init__(self, settings: Settings) -> None:
        self._timeout = settings.dependency_timeout_seconds
        self._contact_points = settings.cassandra_contact_points
        self._port = settings.cassandra_port
        self._keyspace = settings.cassandra_keyspace

        self._lock = threading.Lock()
        self._cluster: Cluster | None = None
        self._session = None
        self._comentarios_por_partido = None

    def close(self) -> None:
        with self._lock:
            self._reset()

    def _reset(self) -> None:
        if self._session is not None:
            try:
                self._session.shutdown()
            except Exception:
                pass

        if self._cluster is not None:
            try:
                self._cluster.shutdown()
            except Exception:
                pass

        self._cluster = None
        self._session = None
        self._comentarios_por_partido = None

    def _ensure_session(self):
        if self._session is not None:
            return self._session

        with self._lock:
            if self._session is not None:
                return self._session

            cluster = Cluster(
                contact_points=self._contact_points,
                port=self._port,
                connect_timeout=self._timeout,
                control_connection_timeout=self._timeout,
            )

            try:
                session = cluster.connect(self._keyspace)
                session.default_timeout = self._timeout

                prepared = session.prepare(
                    COMENTARIOS_POR_PARTIDO_CQL
                )
            except Exception as error:
                try:
                    cluster.shutdown()
                except Exception:
                    pass

                raise self._translate_connect_error(
                    error
                ) from error

            self._cluster = cluster
            self._session = session
            self._comentarios_por_partido = prepared

            logger.info(
                "Sesión Cassandra establecida en keyspace %s",
                self._keyspace,
            )

            return self._session

    def _translate_connect_error(
        self,
        error: Exception,
    ) -> Exception:
        logger.warning(
            "No se pudo abrir la sesión Cassandra: %s",
            type(error).__name__,
        )

        if isinstance(error, NoHostAvailable):
            causes = list(
                getattr(error, "errors", {}).values()
            )

            if any(
                isinstance(cause, AuthenticationFailed)
                for cause in causes
            ):
                return DependencyMisconfiguredError(
                    self.dependency_name,
                    "autenticacion",
                )

            if any(
                isinstance(cause, OperationTimedOut)
                for cause in causes
            ):
                return DependencyTimeoutError(
                    self.dependency_name
                )

            return DependencyUnavailableError(
                self.dependency_name
            )

        if isinstance(error, OperationTimedOut):
            return DependencyTimeoutError(
                self.dependency_name
            )

        if isinstance(error, Unauthorized):
            return DependencyMisconfiguredError(
                self.dependency_name,
                "autorizacion",
            )

        if isinstance(error, InvalidRequest):
            # Keyspace inexistente o tabla no configurada.
            return DependencyMisconfiguredError(
                self.dependency_name,
                "contexto",
            )

        return DependencyUnavailableError(
            self.dependency_name
        )

    def ping(self) -> str:
        """Chequeo liviano para readiness (Hito 11)."""
        session = self._ensure_session()

        try:
            row = session.execute(
                "SELECT release_version FROM system.local",
                timeout=self._timeout,
            ).one()
        except (OperationTimedOut, ReadTimeout) as error:
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except NoHostAvailable as error:
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error

        version = row.release_version if row else "desconocida"
        return f"cql ok; keyspace {self._keyspace}; version {version}"

    def get_comentarios_por_partido(
        self,
        partido_codigo: str,
        bucket_10min: str,
        limit: int,
        page_state: str | None,
    ) -> dict[str, Any]:
        paging_state = self._decode_page_state(page_state)

        session = self._ensure_session()

        statement = self._comentarios_por_partido.bind(
            (partido_codigo, bucket_10min)
        )
        statement.fetch_size = limit

        try:
            result = session.execute(
                statement,
                timeout=self._timeout,
                paging_state=paging_state,
            )
        except (OperationTimedOut, ReadTimeout) as error:
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except NoHostAvailable as error:
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error
        except InvalidRequest as error:
            if page_state is not None:
                raise ApiError(
                    status_code=422,
                    code="PAGINACION_INVALIDA",
                    message=(
                        "El page_state recibido no es válido "
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
                    "un formato válido."
                ),
            ) from error
