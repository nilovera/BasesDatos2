"""Adaptador HTTP de las lecturas de transmisión."""
from fastapi import APIRouter, Query
from pymongo.errors import PyMongoError

from .cassandra_client import get_cassandra_session
from .cassandra_service import CassandraCommentService
from .config import settings
from .database import get_client
from .errors import DomainError
from .influx_client import get_influx_client
from .redis_client import RedisError, get_redis_client
from .repository import MongoRepository
from . import live_service

router = APIRouter(prefix="/api/v1/directo", tags=["Transmisión"])


@router.get("")
def transmission(simulacion_id: str | None = Query(None, alias="simulacionId")):
    try:
        return live_service.transmission(
            MongoRepository(get_client()), get_redis_client(), simulacion_id, (RedisError,)
        )
    except PyMongoError as error:
        raise DomainError(503, "OFFICIAL_STORE_UNAVAILABLE", "No se pudo actualizar el partido") from error


@router.get("/comentarios")
def transmission_comments(simulacion_id: str = Query(alias="simulacionId")):
    try:
        return live_service.transmission_comments(
            get_client()[settings.mongodb_database], simulacion_id,
            CassandraCommentService(get_cassandra_session()),
        )
    except PyMongoError as error:
        raise DomainError(503, "OFFICIAL_STORE_UNAVAILABLE", "No se pudo consultar el partido") from error


@router.get("/cancha")
def transmission_pitch(
    simulacion_id: str = Query(alias="simulacionId"),
    jugador_id: str | None = Query(None, alias="jugadorId"),
    equipo_id: str | None = Query(None, alias="equipoId"),
):
    try:
        doc = live_service.simulation_document(get_client()[settings.mongodb_database], simulacion_id)
        queries = live_service.telemetry_queries(doc["partidoId"], jugador_id, equipo_id)
        client = get_influx_client()
        results = [client.query(settings.influxdb_detail_database, query) for query in queries]
        return {"posiciones": results[0], "pelota": results[1][0] if results[1] else None,
                "celdas": results[2], "columnas": 20, "filas": 12}
    except PyMongoError as error:
        raise DomainError(503, "OFFICIAL_STORE_UNAVAILABLE", "No se pudo consultar el partido") from error
