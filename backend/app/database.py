from pymongo import MongoClient

from .config import settings


_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(
            settings.mongodb_uri,
            appname="fixture2030-api",
            serverSelectionTimeoutMS=settings.mongodb_timeout_ms,
            uuidRepresentation="standard",
        )
    return _client


def close_client():
    global _client
    if _client is not None:
        _client.close()
        _client = None
