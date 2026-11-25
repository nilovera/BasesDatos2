from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from .config import settings


def _password():
    path = Path(settings.datamart_password_file)
    return path.read_text(encoding="utf-8").strip()


def connect_datamart():
    return psycopg.connect(
        host=settings.datamart_host,
        port=settings.datamart_port,
        dbname=settings.datamart_database,
        user=settings.datamart_user,
        password=_password(),
        connect_timeout=settings.datamart_timeout_seconds,
        row_factory=dict_row,
    )

