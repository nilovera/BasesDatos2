from typing import Any


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
        dependency: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.dependency = dependency


class ResourceNotFoundError(ApiError):
    def __init__(
        self,
        resource: str,
        identifier: str,
    ) -> None:
        super().__init__(
            status_code=404,
            code="RECURSO_NO_ENCONTRADO",
            message=f"No se encontró {resource} con identificador {identifier}.",
        )


class DependencyUnavailableError(ApiError):
    def __init__(self, dependency: str) -> None:
        super().__init__(
            status_code=503,
            code="DEPENDENCIA_NO_DISPONIBLE",
            message=(
                f"La dependencia {dependency} no se encuentra disponible."
            ),
            dependency=dependency,
        )


class DependencyTimeoutError(ApiError):
    def __init__(self, dependency: str) -> None:
        super().__init__(
            status_code=504,
            code="TIEMPO_DE_ESPERA_AGOTADO",
            message=(
                f"La dependencia {dependency} excedió el tiempo de espera."
            ),
            dependency=dependency,
        )

class DependencyMisconfiguredError(ApiError):
    """La dependencia responde, pero rechaza la identidad o el contexto.

    Se diferencia de DependencyUnavailableError para que el cliente y los
    logs distingan "el motor no responde" de "el motor responde pero la
    configuración de la API no le permite operar" (Hito 11, RF17).
    No incluye mensajes del driver para no filtrar datos de conexión.
    """

    MOTIVOS = {
        "autenticacion": "La dependencia rechazó la identidad configurada.",
        "autorizacion": "La identidad configurada no tiene permisos suficientes.",
        "contexto": "El contexto configurado (database, keyspace o namespace) no existe.",
    }

    def __init__(self, dependency: str, motivo: str) -> None:
        super().__init__(
            status_code=503,
            code="DEPENDENCIA_MAL_CONFIGURADA",
            message=(
                f"La dependencia {dependency} respondió, pero no pudo "
                "utilizarse con la configuración actual."
            ),
            details={
                "dependencia": dependency,
                "capa": motivo,
                "descripcion": self.MOTIVOS.get(motivo, motivo),
            },
            dependency=dependency,
        )
