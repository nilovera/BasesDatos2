import logging
from typing import Any

from neo4j import GraphDatabase, Query
from neo4j.exceptions import (
    Neo4jError,
    ServiceUnavailable,
    SessionExpired,
)

from app.config.settings import Settings
from app.exceptions import (
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
        except Neo4jError as error:
            logger.warning(
                "Error del driver Neo4j: %s",
                type(error).__name__,
            )
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error

