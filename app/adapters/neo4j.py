import logging
from typing import Any

from neo4j import GraphDatabase, Query
from neo4j.exceptions import (
    AuthError,
    ClientError,
    Forbidden,
    Neo4jError,
    ServiceUnavailable,
    SessionExpired,
)

from app.config.settings import Settings
from app.exceptions import (
    DependencyMisconfiguredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


logger = logging.getLogger("fixture2030.neo4j")


PARTIDO_EVENTOS_QUERY = """
MATCH (partido:Partido {codigo: $codigo})

OPTIONAL MATCH
    (partido)-[:DISPUTA]->(equipo:Equipo)

WITH partido, equipo
ORDER BY equipo.codigo

WITH
    partido,
    collect(
        equipo {
            .codigo,
            .nombre,
            .confederacion
        }
    ) AS equipos

OPTIONAL MATCH
    (partido)-[:SE_JUEGA_EN]->(sede:Sede)

WITH
    partido,
    equipos,
    head(
        collect(
            sede {
                .codigo,
                .nombre
            }
        )
    ) AS sede

OPTIONAL MATCH
    (evento:Evento)-[:OCURRE_EN]->(partido)

WITH
    partido,
    equipos,
    sede,
    evento

ORDER BY evento.minuto, evento.codigo

RETURN
    partido {
        .codigo,
        .fecha,
        .fase
    } AS partido,
    equipos,
    sede,
    collect(
        evento {
            .codigo,
            .tipo,
            .minuto
        }
    ) AS eventos
"""


class Neo4jAdapter:
    dependency_name = "Neo4j"

    def __init__(self, settings: Settings) -> None:
        self._database = settings.neo4j_database
        self._timeout_seconds = (
            settings.dependency_timeout_seconds
        )

        self._driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(
                settings.neo4j_username,
                settings.neo4j_password.get_secret_value(),
            ),
            connection_timeout=self._timeout_seconds,
        )

    def close(self) -> None:
        self._driver.close()

    def get_partido_eventos(
        self,
        codigo: str,
    ) -> dict[str, Any] | None:
        try:
            with self._driver.session(
                database=self._database
            ) as session:
                result = session.run(
                    Query(
                        PARTIDO_EVENTOS_QUERY,
                        timeout=self._timeout_seconds,
                    ),
                    codigo=codigo,
                )

                record = result.single()

                if record is None:
                    return None

                return record.data()
        except TimeoutError as error:
            logger.warning(
                "Neo4j excediÃ³ el tiempo de espera: %s",
                type(error).__name__,
            )
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except (
            ServiceUnavailable,
            SessionExpired,
        ) as error:
            logger.warning(
                "Neo4j no disponible: %s",
                type(error).__name__,
            )
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error
        except (AuthError, Forbidden, ClientError) as error:
            raise self._translate_client_error(
                error
            ) from error
        except Neo4jError as error:
            logger.warning(
                "Error del driver Neo4j: %s",
                type(error).__name__,
            )
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error

    def ping(self) -> str:
        """Chequeo liviano para readiness (Hito 11).

        Bolt + autenticación + database seleccionada + retorno constante.
        """
        try:
            with self._driver.session(
                database=self._database
            ) as session:
                session.run(
                    Query(
                        "RETURN 1 AS ok",
                        timeout=self._timeout_seconds,
                    )
                ).single()
        except TimeoutError as error:
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except (ServiceUnavailable, SessionExpired) as error:
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error
        except (AuthError, Forbidden, ClientError) as error:
            raise self._translate_client_error(
                error
            ) from error
        except Neo4jError as error:
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error

        return f"bolt ok; database {self._database}"

    def _translate_client_error(
        self,
        error: Neo4jError,
    ) -> Exception:
        code = getattr(error, "code", "") or ""
        logger.warning(
            "Neo4j rechazó la operación: %s %s",
            type(error).__name__,
            code,
        )
        if isinstance(error, AuthError) or "Security.Unauthorized" in code:
            return DependencyMisconfiguredError(
                self.dependency_name,
                "autenticacion",
            )
        if isinstance(error, Forbidden) or "Security.Forbidden" in code:
            return DependencyMisconfiguredError(
                self.dependency_name,
                "autorizacion",
            )
        if "DatabaseNotFound" in code:
            return DependencyMisconfiguredError(
                self.dependency_name,
                "contexto",
            )
        if "TransactionTimedOut" in code:
            return DependencyTimeoutError(
                self.dependency_name
            )
        return DependencyUnavailableError(
            self.dependency_name
        )

