from typing import Any

import httpx

from app.config.settings import Settings
from app.exceptions import (
    DependencyMisconfiguredError,
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

    def _raise_for_status(
        self,
        response: httpx.Response,
    ) -> None:
        """Traduce respuestas HTTP de error a errores diferenciados.

        Hasta el Hito 10 cualquier status >= 400 se informaba como
        "dependencia no disponible". Desde el Hito 11 se distingue
        token inválido (401), falta de permisos (403) y database
        inexistente (404 / mensaje "not found"), sin exponer el token.
        """
        status = response.status_code

        if status < 400:
            return

        if status == 401:
            raise DependencyMisconfiguredError(
                "InfluxDB",
                "autenticacion",
            )

        if status == 403:
            raise DependencyMisconfiguredError(
                "InfluxDB",
                "autorizacion",
            )

        body = response.text.lower()

        if status == 404 or (
            "database" in body and "not found" in body
        ):
            raise DependencyMisconfiguredError(
                "InfluxDB",
                "contexto",
            )

        raise DependencyUnavailableError("InfluxDB")

    def ping(self) -> str:
        """Chequeo liviano para readiness (Hito 11).

        /health con token y una consulta de retorno constante sobre la
        database de detalle (verifica autorización y contexto).
        """
        try:
            health = self._client.get("/health")
            self._raise_for_status(health)

            query = self._client.post(
                "/api/v3/query_sql",
                json={
                    "db": self._detail_database,
                    "q": "SELECT 1 AS ok",
                    "format": "json",
                },
            )
            self._raise_for_status(query)
        except httpx.TimeoutException as error:
            raise DependencyTimeoutError(
                "InfluxDB"
            ) from error
        except httpx.RequestError as error:
            raise DependencyUnavailableError(
                "InfluxDB"
            ) from error

        return f"health ok; database {self._detail_database}"

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

        self._raise_for_status(response)

        payload = response.json()

        if not isinstance(payload, list):
            raise DependencyUnavailableError(
                "InfluxDB"
            )

        return payload