from typing import Any

import httpx

from app.config.settings import Settings
from app.exceptions import (
    DependencyTimeoutError,
    DependencyUnavailableError,
)


class InfluxDBAdapter:
    def __init__(self, settings: Settings) -> None:
        self._detail_database = (
            settings.influxdb_detail_database
        )
        self._historical_database = (
            settings.influxdb_historical_database
        )

        token = (
            settings.influxdb_token.get_secret_value()
        )

        self._client = httpx.Client(
            base_url=str(
                settings.influxdb_url
            ).rstrip("/"),
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=settings.dependency_timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    def get_estadisticas(
        self,
        partido_codigo: str,
        equipo_id: str | None,
        desde: str,
        hasta: str,
        granularidad: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        if granularidad == "detalle":
            database = self._detail_database
            table = "estadisticas_equipo"
            columns = """
                time,
                equipo_id,
                posesion_pct,
                pases_intervalo,
                tiros_acumulados
            """
        else:
            database = self._historical_database
            table = "resumen_equipo_minuto"
            columns = """
                time,
                equipo_id,
                posesion_promedio,
                pases_total,
                muestras
            """

        equipo_filter = ""

        params: dict[str, Any] = {
            "partido_id": partido_codigo,
            "desde": desde,
            "hasta": hasta,
        }

        if equipo_id is not None:
            equipo_filter = (
                "AND equipo_id = $equipo_id"
            )
            params["equipo_id"] = equipo_id

        query_limit = limit + 1

        query = f"""
            SELECT {columns}
            FROM {table}
            WHERE partido_id = $partido_id
              AND time >= $desde
              AND time < $hasta
              {equipo_filter}
            ORDER BY time ASC, equipo_id ASC
            LIMIT {query_limit}
        """

        try:
            response = self._client.post(
                "/api/v3/query_sql",
                json={
                    "db": database,
                    "q": query,
                    "params": params,
                    "format": "json",
                },
            )
        except httpx.TimeoutException as error:
            raise DependencyTimeoutError(
                "InfluxDB"
            ) from error
        except httpx.RequestError as error:
            raise DependencyUnavailableError(
                "InfluxDB"
            ) from error

        if response.status_code >= 400:
            raise DependencyUnavailableError(
                "InfluxDB"
            )

        payload = response.json()

        if not isinstance(payload, list):
            raise DependencyUnavailableError(
                "InfluxDB"
            )

        return payload