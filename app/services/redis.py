from app.adapters.redis import RedisAdapter
from app.exceptions import ApiError
from app.schemas.redis import (
    CierreSesionResponse,
    SesionResponse,
)


class RedisService:
    def __init__(
        self,
        adapter: RedisAdapter,
    ) -> None:
        self._adapter = adapter

    def get_sesion(
        self,
        sesion_id: str,
    ) -> SesionResponse:
        result = self._adapter.get_sesion(
            sesion_id
        )

        if result is None:
            self._raise_not_found(sesion_id)

        return SesionResponse(**result)

    def cerrar_sesion(
        self,
        sesion_id: str,
    ) -> CierreSesionResponse:
        cerrada = self._adapter.cerrar_sesion(
            sesion_id
        )

        if not cerrada:
            self._raise_not_found(sesion_id)

        return CierreSesionResponse(
            sesion_id=sesion_id,
            cerrada=True,
            mensaje="La sesión fue cerrada correctamente.",
        )

    @staticmethod
    def _raise_not_found(
        sesion_id: str,
    ) -> None:
        raise ApiError(
            status_code=404,
            code="SESION_NO_ENCONTRADA_O_EXPIRADA",
            message=(
                "La sesión no existe o su tiempo "
                f"de vida expiró: {sesion_id}."
            ),
        )