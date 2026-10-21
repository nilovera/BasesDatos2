import logging
from typing import Any

from pymongo import ASCENDING, MongoClient
from pymongo.errors import (
    ExecutionTimeout,
    NetworkTimeout,
    OperationFailure,
    PyMongoError,
)

from app.config.settings import Settings
from app.exceptions import (
    DependencyMisconfiguredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


# Códigos de error del servidor MongoDB relevantes para el diagnóstico.
MONGO_AUTH_FAILED = 18
MONGO_UNAUTHORIZED = 13


logger = logging.getLogger("fixture2030.mongodb")


class MongoAdapter:
    dependency_name = "MongoDB"

    def __init__(self, settings: Settings) -> None:
        self._timeout_ms = int(
            settings.dependency_timeout_seconds * 1000
        )

        self._client = MongoClient(
            host=settings.mongodb_host,
            port=settings.mongodb_port,
            username=settings.mongodb_username,
            password=(
                settings.mongodb_password.get_secret_value()
            ),
            authSource=settings.mongodb_auth_source,
            serverSelectionTimeoutMS=self._timeout_ms,
            connectTimeoutMS=self._timeout_ms,
            socketTimeoutMS=self._timeout_ms,
        )

        self._database = self._client[
            settings.mongodb_database
        ]

    def close(self) -> None:
        self._client.close()

    def ping(self) -> str:
        """Chequeo liviano para readiness (Hito 11).

        Verifica autenticación (ping sobre la conexión autenticada) y
        contexto (que la database tenga la colección equipos). No lee
        documentos de dominio.
        """
        try:
            self._client.admin.command(
                "ping",
                maxTimeMS=self._timeout_ms,
            )
            colecciones = self._database.list_collection_names(
                filter={"name": "equipos"},
                maxTimeMS=self._timeout_ms,
            )
        except (ExecutionTimeout, NetworkTimeout) as error:
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except OperationFailure as error:
            raise self._translate_operation_failure(
                error
            ) from error
        except PyMongoError as error:
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error

        if not colecciones:
            # MongoDB no falla ante una database inexistente: la crea de
            # forma perezosa y devuelve vacío. Por eso se valida aquí.
            raise DependencyMisconfiguredError(
                self.dependency_name,
                "contexto",
            )

        return "ping ok; coleccion equipos presente"

    def _translate_operation_failure(
        self,
        error: OperationFailure,
    ) -> Exception:
        logger.warning(
            "MongoDB rechazó la operación: codigo=%s",
            error.code,
        )
        if error.code == MONGO_AUTH_FAILED:
            return DependencyMisconfiguredError(
                self.dependency_name,
                "autenticacion",
            )
        if error.code == MONGO_UNAUTHORIZED:
            return DependencyMisconfiguredError(
                self.dependency_name,
                "autorizacion",
            )
        return DependencyUnavailableError(
            self.dependency_name
        )

    def get_equipo(
        self,
        codigo: str,
    ) -> dict[str, Any] | None:
        try:
            return self._database["equipos"].find_one(
                {"_id": codigo},
                {
                    "_id": 1,
                    "nombre": 1,
                    "confederacion": 1,
                    "ranking": 1,
                },
                max_time_ms=self._timeout_ms,
            )
        except (ExecutionTimeout, NetworkTimeout) as error:
            logger.warning(
                "MongoDB excedió el tiempo de espera: %s",
                type(error).__name__,
            )
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except OperationFailure as error:
            raise self._translate_operation_failure(
                error
            ) from error
        except PyMongoError as error:
            logger.warning(
                "MongoDB no disponible: %s",
                type(error).__name__,
            )
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error

    def list_jugadores(
        self,
        equipo_codigo: str,
        posicion: str | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict[str, Any]], bool]:
        filters: dict[str, Any] = {
            "equipo_id": equipo_codigo
        }

        if posicion is not None:
            filters["posicion"] = posicion

        if cursor is not None:
            filters["_id"] = {"$gt": cursor}

        try:
            query = (
                self._database["jugadores"]
                .find(
                    filters,
                    {
                        "_id": 1,
                        "nombre": 1,
                        "fecha_nacimiento": 1,
                        "posicion": 1,
                        "equipo_id": 1,
                    },
                )
                .sort("_id", ASCENDING)
                .limit(limit + 1)
                .max_time_ms(self._timeout_ms)
            )

            documents = list(query)
            has_more = len(documents) > limit

            return documents[:limit], has_more
        except (ExecutionTimeout, NetworkTimeout) as error:
            logger.warning(
                "MongoDB excedió el tiempo de espera: %s",
                type(error).__name__,
            )
            raise DependencyTimeoutError(
                self.dependency_name
            ) from error
        except OperationFailure as error:
            raise self._translate_operation_failure(
                error
            ) from error
        except PyMongoError as error:
            logger.warning(
                "MongoDB no disponible: %s",
                type(error).__name__,
            )
            raise DependencyUnavailableError(
                self.dependency_name
            ) from error