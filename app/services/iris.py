from app.adapters.iris import IRISAdapter
from app.exceptions import ApiError
from app.schemas.iris import PartidoIRISResponse


class IRISService:
    def __init__(
        self,
        adapter: IRISAdapter,
    ) -> None:
        self._adapter = adapter

    def get_partido_detalle(
        self,
        codigo: str,
    ) -> PartidoIRISResponse:
        result = self._adapter.get_partido_detalle(
            codigo
        )

        if result is None:
            raise ApiError(
                status_code=404,
                code="PARTIDO_IRIS_NO_ENCONTRADO",
                message=(
                    "No se encontró el partido "
                    f"persistente {codigo} en IRIS."
                ),
            )

        return PartidoIRISResponse(**result)