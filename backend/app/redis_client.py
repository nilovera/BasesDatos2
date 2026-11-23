from functools import lru_cache

from redis import Redis
from redis.exceptions import RedisError

from .config import settings


@lru_cache(maxsize=1)
def get_redis_client():
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=settings.redis_timeout_seconds,
        socket_timeout=settings.redis_timeout_seconds,
        health_check_interval=30,
    )


def close_redis_client():
    if get_redis_client.cache_info().currsize:
        get_redis_client().close()
        get_redis_client.cache_clear()


__all__ = ["RedisError", "close_redis_client", "get_redis_client"]
