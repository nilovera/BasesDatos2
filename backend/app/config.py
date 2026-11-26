import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str = os.getenv(
        "MONGODB_URI", "mongodb://localhost:27017/?directConnection=true"
    )
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "fixture2030")
    mongodb_timeout_ms: int = int(os.getenv("MONGODB_TIMEOUT_MS", "3000"))
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_timeout_seconds: float = float(os.getenv("REDIS_TIMEOUT_SECONDS", "1.0"))
    match_cache_ttl_seconds: int = int(os.getenv("MATCH_CACHE_TTL_SECONDS", "60"))
    outbox_poll_seconds: float = float(os.getenv("OUTBOX_POLL_SECONDS", "1.0"))
    outbox_lease_seconds: int = int(os.getenv("OUTBOX_LEASE_SECONDS", "30"))
    outbox_max_attempts: int = int(os.getenv("OUTBOX_MAX_ATTEMPTS", "8"))
    outbox_retention_days: int = int(os.getenv("OUTBOX_RETENTION_DAYS", "30"))
    outbox_metrics_port: int = int(os.getenv("OUTBOX_METRICS_PORT", "9101"))
    session_default_ttl_seconds: int = int(os.getenv("SESSION_DEFAULT_TTL_SECONDS", "1800"))
    cassandra_host: str = os.getenv("CASSANDRA_HOST", "localhost")
    cassandra_port: int = int(os.getenv("CASSANDRA_PORT", "9042"))
    cassandra_keyspace: str = os.getenv("CASSANDRA_KEYSPACE", "fixture2030_comments")
    cassandra_timeout_seconds: float = float(os.getenv("CASSANDRA_TIMEOUT_SECONDS", "3.0"))
    influxdb_url: str = os.getenv("INFLUXDB_URL", "http://localhost:8181")
    influxdb_token_file: str = os.getenv(
        "INFLUXDB_TOKEN_FILE", ".secretos/influxdb-admin-token.txt"
    )
    influxdb_detail_database: str = os.getenv(
        "INFLUXDB_DETAIL_DATABASE", "fixture2030-detalle"
    )
    influxdb_historical_database: str = os.getenv(
        "INFLUXDB_HISTORICAL_DATABASE", "fixture2030-historico"
    )
    influxdb_timeout_seconds: float = float(
        os.getenv("INFLUXDB_TIMEOUT_SECONDS", "3.0")
    )
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password_file: str = os.getenv(
        "NEO4J_PASSWORD_FILE", ".secretos/neo4j-password.txt"
    )
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    neo4j_timeout_seconds: float = float(
        os.getenv("NEO4J_TIMEOUT_SECONDS", "3.0")
    )
    datamart_host: str = os.getenv("DATAMART_HOST", "localhost")
    datamart_port: int = int(os.getenv("DATAMART_PORT", "5433"))
    datamart_database: str = os.getenv("DATAMART_DATABASE", "fixture2030_analytics")
    datamart_user: str = os.getenv("DATAMART_USER", "fixture2030")
    datamart_password_file: str = os.getenv(
        "DATAMART_PASSWORD_FILE", ".secretos/datamart-password.txt"
    )
    datamart_timeout_seconds: int = int(os.getenv("DATAMART_TIMEOUT_SECONDS", "3"))
    datamart_pool_min_size: int = int(os.getenv("DATAMART_POOL_MIN_SIZE", "2"))
    datamart_pool_max_size: int = int(os.getenv("DATAMART_POOL_MAX_SIZE", "10"))
    datamart_pool_timeout_seconds: float = float(
        os.getenv("DATAMART_POOL_TIMEOUT_SECONDS", "3.0")
    )
    datamart_pool_max_idle_seconds: float = float(
        os.getenv("DATAMART_POOL_MAX_IDLE_SECONDS", "300.0")
    )


settings = Settings()
