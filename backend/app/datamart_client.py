from pathlib import Path
from threading import Lock

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import settings


_pool = None
_pool_lock = Lock()


def _password():
    path = Path(settings.datamart_password_file)
    return path.read_text(encoding="utf-8").strip()


def get_datamart_pool():
    global _pool
    if _pool is None or _pool.closed:
        with _pool_lock:
            if _pool is None or _pool.closed:
                _pool = ConnectionPool(
                    conninfo="",
                    kwargs={
                        "host": settings.datamart_host,
                        "port": settings.datamart_port,
                        "dbname": settings.datamart_database,
                        "user": settings.datamart_user,
                        "password": _password(),
                        "connect_timeout": settings.datamart_timeout_seconds,
                        "row_factory": dict_row,
                    },
                    min_size=settings.datamart_pool_min_size,
                    max_size=settings.datamart_pool_max_size,
                    timeout=settings.datamart_pool_timeout_seconds,
                    max_idle=settings.datamart_pool_max_idle_seconds,
                    name="fixture2030-datamart",
                    open=True,
                )
    return _pool


def datamart_connection():
    return get_datamart_pool().connection(
        timeout=settings.datamart_pool_timeout_seconds
    )


def close_datamart_pool():
    global _pool
    if _pool is not None:
        _pool.close(timeout=settings.datamart_timeout_seconds)
        _pool = None

