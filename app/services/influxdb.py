from datetime import datetime, timedelta, timezone

from app.adapters.influxdb import InfluxDBAdapter
from app.exceptions import ApiError
from app.schemas.influxdb import (
    EstadisticasPartidoResponse,
    MetadataEstadisticas,
    PuntoDetalleResponse,
    Resumen15MinutosResponse,
)


class InfluxDBService:
    def __init__(
        self,
        adapter: InfluxDBAdapter,
    ) -> None:
        self._adapter = adapter

    def get_estadisticas(
        self,
        partido_codigo: str,
        equipo_id: str | None,
        desde: datetime,
        hasta: datetime,
        granularidad: str,
        limit: int,
    ) -> EstadisticasPartidoResponse:
        self._validate_window(
            desde=desde,
            hasta=hasta,
            granularidad=granularidad,
        )

        desde_utc = desde.astimezone(timezone.utc)
        hasta_utc = hasta.astimezone(timezone.utc)

        rows = self._adapter.get_estadisticas(
            partido_codigo=partido_codigo,
            equipo_id=equipo_id,
            desde=self._format_datetime(desde_utc),
            hasta=self._format_datetime(hasta_utc),
            granularidad=granularidad,
            limit=limit,
        )

        hay_mas = len(rows) > limit
        rows = rows[:limit]

        if granularidad == "detalle":
            datos = [
                PuntoDetalleResponse(**row)
                for row in rows
            ]
            intervalo = "10 segundos"
        else:
            datos = [
                Resumen15MinutosResponse(**row)
                for row in rows
            ]
            intervalo = "15 minutos"

        return EstadisticasPartidoResponse(
            partido_codigo=partido_codigo,
            granularidad=granularidad,
            equipo_id=equipo_id,
            datos=datos,
            metadata=MetadataEstadisticas(
                limite=limit,
                cantidad=len(datos),
                hay_mas=hay_mas,
                desde=desde_utc,
                hasta=hasta_utc,
                intervalo_fuente=intervalo,
            ),
        )

    @staticmethod
    def _validate_window(
        desde: datetime,
        hasta: datetime,
        granularidad: str,
    ) -> None:
        if (
            desde.tzinfo is None
            or hasta.tzinfo is None
        ):
            raise ApiError(
                status_code=422,
                code="VENTANA_TEMPORAL_INVALIDA",
                message=(
                    "Las fechas desde y hasta deben "
                    "incluir zona horaria."
                ),
            )

        if desde >= hasta:
            raise ApiError(
                status_code=422,
                code="VENTANA_TEMPORAL_INVALIDA",
                message=(
                    "La fecha desde debe ser anterior "
                    "a la fecha hasta."
                ),
            )

        duration = hasta - desde

        if (
            granularidad == "detalle"
            and duration > timedelta(hours=24)
        ):
            raise ApiError(
                status_code=422,
                code="VENTANA_TEMPORAL_EXCESIVA",
                message=(
                    "La consulta detallada admite como "
                    "máximo una ventana de 24 horas."
                ),
            )

        if (
            granularidad == "15m"
            and duration > timedelta(days=366)
        ):
            raise ApiError(
                status_code=422,
                code="VENTANA_TEMPORAL_EXCESIVA",
                message=(
                    "La consulta histórica admite como "
                    "máximo una ventana de 366 días."
                ),
            )

    @staticmethod
    def _format_datetime(
        value: datetime,
    ) -> str:
        return (
            value.isoformat()
            .replace("+00:00", "Z")
        )