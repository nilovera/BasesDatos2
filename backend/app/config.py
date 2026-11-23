import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mongodb_uri: str = os.getenv(
        "MONGODB_URI", "mongodb://localhost:27017/?directConnection=true"
    )
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "fixture2030")
    mongodb_timeout_ms: int = int(os.getenv("MONGODB_TIMEOUT_MS", "3000"))


settings = Settings()
