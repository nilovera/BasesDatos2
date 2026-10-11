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