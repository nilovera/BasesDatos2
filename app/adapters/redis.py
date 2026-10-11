from typing import Any

import redis as redis_client
from redis.backoff import NoBackoff
from redis.retry import Retry
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
)
from redis.exceptions import TimeoutError as RedisTimeoutError

from app.config.settings import Settings
from app.exceptions import (
    DependencyTimeoutError,
    DependencyUnavailableError,
)


class RedisAdapter:
    def __init__(self, settings: Settings) -> None:
        self._client = redis_client.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_database,
            decode_responses=True,
            retry=Retry(NoBackoff(), 0),
            socket_connect_timeout=(
                settings.dependency_timeout_seconds
            ),
            socket_timeout=(
                settings.dependency_timeout_seconds
            ),
            health_check_interval=30,
        )

    def close(self) -> None:
        self._client.close()

    def get_sesion(
        self,
        sesion_id: str,
    ) -> dict[str, Any] | None:
        key = self._key(sesion_id)

        try:
            pipeline = self._client.pipeline(
                transaction=False
            )
            pipeline.hgetall(key)
            pipeline.ttl(key)

            data, ttl = pipeline.execute()
        except RedisTimeoutError as error:
            raise DependencyTimeoutError(
                "Redis"
            ) from error
        except RedisConnectionError as error:
            raise DependencyUnavailableError(
                "Redis"
            ) from error

        if not data or ttl <= 0:
            return None

        return {
            "sesion_id": data.get(
                "sesion_id",
                sesion_id,
            ),
            "usuario_id": data.get("usuario_id"),
            "rol": data.get("rol"),
            "ultimo_acceso": data.get(
                "ultimo_acceso"
            ),
            "estado": data.get("estado"),
            "partido_actual": data.get(
                "partido_actual"
            ) or None,
            "acciones": int(
                data.get("acciones", "0")
            ),
            "ttl_segundos": int(ttl),
        }

    def cerrar_sesion(
        self,
        sesion_id: str,
    ) -> bool:
        try:
            eliminadas = self._client.delete(
                self._key(sesion_id)
            )
        except RedisTimeoutError as error:
            raise DependencyTimeoutError(
                "Redis"
            ) from error
        except RedisConnectionError as error:
            raise DependencyUnavailableError(
                "Redis"
            ) from error

        return eliminadas == 1

    @staticmethod
    def _key(sesion_id: str) -> str:
        return f"sesion:{sesion_id}"