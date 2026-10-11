from typing import Any

import iris.dbapi as iris_dbapi

from app.config.settings import Settings
from app.exceptions import (
    DependencyTimeoutError,
    DependencyUnavailableError,
)


class IRISAdapter:
    def __init__(self, settings: Settings) -> None:
        self._host = settings.iris_host
        self._port = settings.iris_port
        self._namespace = settings.iris_namespace
        self._username = settings.iris_username
        self._password = (
            settings.iris_password.get_secret_value()
        )
        self._timeout = max(
            1,
            int(settings.dependency_timeout_seconds),
        )

    def close(self) -> None:
        # Las conexiones se abren y cierran por solicitud.
        return None

    def get_partido_detalle(
        self,
        codigo: str,
    ) -> dict[str, Any] | None:
        connection = None
        cursor = None

        try:
            connection = iris_dbapi.connect(
                self._host,
                self._port,
                self._namespace,
                self._username,
                self._password,
            )

            cursor = connection.cursor()
            cursor.setQueryTimeout(self._timeout)

            cursor.execute(
                """
                SELECT
                    ID,
                    Codigo,
                    FechaHora,
                    EquipoLocalId,
                    EquipoVisitanteId,
                    Estado,
                    ArbitroPrincipal
                FROM Fixture.Partido
                WHERE Codigo = ?
                """,
                [codigo],
            )

            partido_rows = cursor.fetchall()
            partido = partido_rows[0] if partido_rows else None

            if partido is None:
                return None

            partido_id = partido[0]
            arbitro_id = partido[6]
            arbitro = None

            if arbitro_id is not None:
                cursor.execute(
                    """
                    SELECT
                        ID,
                        Documento,
                        Nombre,
                        Nacionalidad,
                        Rol,
                        LicenciaFIFA
                    FROM Fixture.Arbitro
                    WHERE ID = ?
                    """,
                    [arbitro_id],
                )

                arbitro_rows = cursor.fetchall()
                arbitro_row = arbitro_rows[0] if arbitro_rows else None

                if arbitro_row is not None:
                    arbitro = {
                        "id": arbitro_row[0],
                        "documento": arbitro_row[1],
                        "nombre": arbitro_row[2],
                        "nacionalidad": arbitro_row[3],
                        "rol": arbitro_row[4],
                        "licencia_fifa": bool(
                            arbitro_row[5]
                        ),
                    }

            cursor.execute(
                """
                SELECT
                    ID,
                    Tipo,
                    Minuto,
                    Detalle
                FROM Fixture.EventoPartido
                WHERE Partido = ?
                ORDER BY Minuto ASC, ID ASC
                """,
                [partido_id],
            )

            eventos = [
                {
                    "id": str(evento[0]),
                    "tipo": evento[1],
                    "minuto": evento[2],
                    "detalle": evento[3],
                }
                for evento in cursor.fetchall()
            ]

            return {
                "id": partido_id,
                "codigo": partido[1],
                "fecha_hora": partido[2],
                "equipo_local_id": partido[3],
                "equipo_visitante_id": partido[4],
                "estado": partido[5],
                "arbitro_principal": arbitro,
                "eventos": eventos,
            }

        except iris_dbapi.Error as error:
            if "timeout" in str(error).lower():
                raise DependencyTimeoutError(
                    "InterSystems IRIS"
                ) from error

            raise DependencyUnavailableError(
                "InterSystems IRIS"
            ) from error

        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass

            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass