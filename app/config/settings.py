from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str
    app_version: str
    app_env: Literal["local", "test", "production"]
    api_host: str
    api_port: int
    log_level: str
    dependency_timeout_seconds: float
    default_page_size: int
    max_page_size: int

    mongodb_host: str
    mongodb_port: int
    mongodb_database: str
    mongodb_auth_source: str
    mongodb_username: str
    mongodb_password: SecretStr

    neo4j_uri: str
    neo4j_database: str
    neo4j_username: str
    neo4j_password: SecretStr

    cassandra_hosts: str
    cassandra_port: int
    cassandra_keyspace: str

    redis_host: str
    redis_port: int
    redis_database: int

    influxdb_url: str
    influxdb_token: SecretStr
    influxdb_detail_database: str
    influxdb_historical_database: str

    iris_host: str
    iris_port: int
    iris_namespace: str
    iris_username: str
    iris_password: SecretStr

    @property
    def cassandra_contact_points(self) -> list[str]:
        return [
            host.strip()
            for host in self.cassandra_hosts.split(",")
            if host.strip()
        ]

    @model_validator(mode="after")
    def validate_limits(self) -> "Settings":
        if self.default_page_size < 1:
            raise ValueError("DEFAULT_PAGE_SIZE debe ser mayor que cero.")

        if self.max_page_size < self.default_page_size:
            raise ValueError(
                "MAX_PAGE_SIZE no puede ser menor que DEFAULT_PAGE_SIZE."
            )

        if self.dependency_timeout_seconds <= 0:
            raise ValueError(
                "DEPENDENCY_TIMEOUT_SECONDS debe ser mayor que cero."
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()