import queue
import threading
from typing import Any

import iris.dbapi as iris_dbapi

from app.config.settings import Settings
from app.exceptions import (
    DependencyMisconfiguredError,
    DependencyTimeoutError,
    DependencyUnavailableError,
)


DEPENDENCY_NAME = "InterSystems IRIS"


def translate_iris_error(error: Exception) -> Exception:
    """Clasifica errores del driver IRIS sin propagar su mensaje."""
    message = str(error).lower()

    if "timeout" in message or "timed out" in message:
        return DependencyTimeoutError(DEPENDENCY_NAME)

    if "access denied" in message or "authentication" in message:
        return DependencyMisconfiguredError(
            DEPENDENCY_NAME,
            "autenticacion",
        )

    if "namespace" in message:
        return DependencyMisconfiguredError(
            DEPENDENCY_NAME,
            "contexto",
        )

    if "privilege" in message or "not authorized" in message:
        return DependencyMisconfiguredError(
            DEPENDENCY_NAME,
            "autorizacion",
        )

    return DependencyUnavailableError(DEPENDENCY_NAME)


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

        # Hito 12 - optimización: pool de conexiones reutilizables.
        # Abrir una conexión con IRIS cuesta ~19 ms (más de 75 ms con
        # concurrencia) contra ~3 ms de la consulta. Con pool_size > 0
        # se reutilizan hasta pool_size conexiones; con 0 se mantiene el
        # comportamiento original (abrir y cerrar en cada solicitud).
        self._pool_size = max(0, int(settings.iris_pool_size))
        self._pool: queue.LifoQueue = queue.LifoQueue(
            maxsize=max(1, self._pool_size)
        )
        self._creadas = 0
        self._lock = threading.Lock()

    def close(self) -> None:
        # Sin pool no hay nada abierto. Con pool se cierran las inactivas.
        while True:
            try:
                connection = self._pool.get_nowait()
            except queue.Empty:
                break
            try:
                connection.close()
            except Exception:
                pass

    def _acquire(self):
        """Entrega una conexión: del pool si hay, nueva si hay cupo, o espera."""
        if self._pool_size == 0:
            return self._connect()

        try:
            return self._pool.get_nowait()
        except queue.Empty:
            pass

        with self._lock:
            crear = self._creadas < self._pool_size
            if crear:
                self._creadas += 1

        if crear:
            try:
                return self._connect()
            except Exception:
                with self._lock:
                    self._creadas -= 1
                raise

        # Pool lleno y todas en uso: se espera como máximo el timeout
        # de dependencia; si no se libera ninguna, se responde 504.
        try:
            return self._pool.get(timeout=self._timeout)
        except queue.Empty as error:
            raise DependencyTimeoutError(DEPENDENCY_NAME) from error

    def _release(self, connection, sana: bool) -> None:
        """Devuelve la conexión al pool, o la cierra si no hay pool o falló."""
        if self._pool_size > 0 and sana:
            try:
                self._pool.put_nowait(connection)
                return
            except queue.Full:
                pass

        try:
            connection.close()
        except Exception:
            pass

        if self._pool_size > 0:
            with self._lock:
                self._creadas = max(0, self._creadas - 1)

    def _connect(self):
        # timeout acota la espera del handshake con el Superserver
        # (Hito 11, RNF5). Sin él, un host inalcanzable bloqueaba la
        # solicitud durante el timeout por defecto del sistema operativo.
        return iris_dbapi.connect(
            self._host,
            self._port,
            self._namespace,
            self._username,
            self._password,
            timeout=self._timeout,
        )

    def ping(self) -> str:
        """Chequeo liviano para readiness (Hito 11).

        Superserver + autenticación + namespace + retorno constante.
        """
        connection = None
        cursor = None

        try:
            connection = self._connect()
            cursor = connection.cursor()
            cursor.setQueryTimeout(self._timeout)
            cursor.execute("SELECT 1")
            cursor.fetchall()
        except iris_dbapi.Error as error:
            raise translate_iris_error(error) from error
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

        return f"superserver ok; namespace {self._namespace}"

    def get_partido_detalle(
        self,
        codigo: str,
    ) -> dict[str, Any] | None:
        connection = None
        cursor = None
        sana = True

        try:
            connection = self._acquire()

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
            # Una conexión que falló no vuelve al pool.
            sana = False
            raise translate_iris_error(error) from error

        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass

            if connection is not None:
                self._release(connection, sana)