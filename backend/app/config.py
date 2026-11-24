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
    session_default_ttl_seconds: int = int(os.getenv("SESSION_DEFAULT_TTL_SECONDS", "1800"))
    cassandra_host: str = os.getenv("CASSANDRA_HOST", "localhost")
    cassandra_port: int = int(os.getenv("CASSANDRA_PORT", "9042"))
    cassandra_keyspace: str = os.getenv("CASSANDRA_KEYSPACE", "fixture2030_comments")
    cassandra_timeout_seconds: float = float(os.getenv("CASSANDRA_TIMEOUT_SECONDS", "3.0"))


settings = Settings()
