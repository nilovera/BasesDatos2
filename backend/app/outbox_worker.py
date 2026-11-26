import json
import logging
import random
import signal
import socket
import threading
import time
from datetime import datetime, timedelta, timezone

from prometheus_client import start_http_server
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError

from .config import settings
from .database import close_client, get_client
from .metrics import (
    CACHE_INVALIDATIONS,
    OUTBOX_FAILED,
    OUTBOX_OLDEST_SECONDS,
    OUTBOX_PENDING,
    OUTBOX_PUBLISHED,
    OUTBOX_RETRIES,
)
from .redis_client import close_redis_client, get_redis_client
from .neo4j_client import close_neo4j_client, get_neo4j_client
from .neo4j_service import Neo4jGraphService


LOGGER = logging.getLogger("fixture2030.outbox")
STOP = threading.Event()

PROJECT_EVENT_LUA = """
if redis.call('HEXISTS', KEYS[1], ARGV[1]) == 1 then
    return 0
end
local invalidated = redis.call('DEL', KEYS[2])
local result = cjson.decode(ARGV[5])['resultado']
redis.call(
    'HSET', KEYS[4],
    'estado', result['estadoPartido'],
    'local', tostring(result['marcador']['local']),
    'visitante', tostring(result['marcador']['visitante']),
    'ultimaSecuencia', ARGV[4],
    'actualizadoEn', ARGV[6]
)
redis.call(
    'XADD', KEYS[3], 'MAXLEN', '~', 1000, '*',
    'eventoId', ARGV[1],
    'partidoId', ARGV[2],
    'tipo', ARGV[3],
    'secuencia', ARGV[4],
    'payload', ARGV[5]
)
redis.call('HSET', KEYS[1], ARGV[1], ARGV[6])
return invalidated + 1
"""


def _as_utc(value):
    """Normaliza fechas BSON; PyMongo devuelve datetimes naive en UTC por defecto."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class OutboxWorker:
    def __init__(self, collection, redis_client, graph_service=None, worker_id=None):
        self.collection = collection
        self.redis = redis_client
        self.graph = graph_service
        self.worker_id = worker_id or f"{socket.gethostname()}-{id(self):x}"

    def claim(self):
        now = datetime.now(timezone.utc)
        lease_until = now + timedelta(seconds=settings.outbox_lease_seconds)
        return self.collection.find_one_and_update(
            {
                "$or": [
                    {"estado": "PENDIENTE", "proximoIntentoEn": {"$lte": now}},
                    {"estado": "PROCESANDO", "bloqueo.hasta": {"$lte": now}},
                ]
            },
            {
                "$set": {
                    "estado": "PROCESANDO",
                    "bloqueo": {"workerId": self.worker_id, "hasta": lease_until},
                    "actualizadoEn": now,
                },
                "$inc": {"intentos": 1},
            },
            sort=[("creadoEn", ASCENDING), ("outboxId", ASCENDING)],
            return_document=ReturnDocument.AFTER,
        )

    def project(self, message):
        published_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return int(
            self.redis.eval(
                PROJECT_EVENT_LUA,
                4,
                "outbox:procesados",
                f"cache:partido:{message['partidoId']}",
                f"eventos:partido:{message['partidoId']}",
                f"marcador:partido:{message['partidoId']}",
                message["eventoId"],
                message["partidoId"],
                message["tipo"],
                str(int(message["secuencia"])),
                json.dumps(message["payload"], ensure_ascii=False, separators=(",", ":")),
                published_at,
            )
        )

    def project_graph(self, message):
        if self.graph is not None:
            self.graph.project_official_event(message)

    def complete(self, message):
        now = datetime.now(timezone.utc)
        result = self.collection.update_one(
            {
                "_id": message["_id"],
                "estado": "PROCESANDO",
                "bloqueo.workerId": self.worker_id,
            },
            {
                "$set": {
                    "estado": "PUBLICADO",
                    "publicadoEn": now,
                    "expiraEn": now + timedelta(days=settings.outbox_retention_days),
                    "proximoIntentoEn": None,
                    "ultimoError": None,
                    "actualizadoEn": now,
                },
                "$unset": {"bloqueo": ""},
            },
        )
        if result.modified_count != 1:
            raise RuntimeError("se perdio el lease antes de confirmar la Outbox")

    def fail(self, message, error):
        now = datetime.now(timezone.utc)
        attempts = int(message["intentos"])
        permanent = attempts >= settings.outbox_max_attempts
        delay = min(60.0, 2 ** max(0, attempts - 1))
        delay += random.uniform(0, delay * 0.2)
        update = {
            "estado": "FALLIDO" if permanent else "PENDIENTE",
            "proximoIntentoEn": None if permanent else now + timedelta(seconds=delay),
            "ultimoError": f"{type(error).__name__}: {error}"[:500],
            "actualizadoEn": now,
        }
        self.collection.update_one(
            {"_id": message["_id"], "bloqueo.workerId": self.worker_id},
            {"$set": update, "$unset": {"bloqueo": ""}},
        )
        if not permanent:
            OUTBOX_RETRIES.inc()

    def refresh_metrics(self):
        now = datetime.now(timezone.utc)
        pending = self.collection.count_documents(
            {"estado": {"$in": ["PENDIENTE", "PROCESANDO"]}}
        )
        failed = self.collection.count_documents({"estado": "FALLIDO"})
        oldest = self.collection.find_one(
            {"estado": {"$in": ["PENDIENTE", "PROCESANDO"]}},
            {"creadoEn": 1},
            sort=[("creadoEn", ASCENDING)],
        )
        age = (
            max(0.0, (now - _as_utc(oldest["creadoEn"])).total_seconds())
            if oldest
            else 0.0
        )
        OUTBOX_PENDING.labels("redis").set(pending)
        OUTBOX_FAILED.labels("redis").set(failed)
        OUTBOX_OLDEST_SECONDS.labels("redis").set(age)

    def run_once(self):
        message = self.claim()
        if message is None:
            self.refresh_metrics()
            return False
        try:
            projection = self.project(message)
            self.project_graph(message)
            self.complete(message)
            OUTBOX_PUBLISHED.labels("REPLAY" if projection == 0 else "NEW").inc()
            if projection > 0:
                CACHE_INVALIDATIONS.labels(
                    "DELETED" if projection == 2 else "ABSENT"
                ).inc()
        except Exception as error:
            LOGGER.warning("outboxId=%s fallo=%s", message.get("outboxId"), type(error).__name__)
            self.fail(message, error)
        self.refresh_metrics()
        return True

    def run_forever(self):
        while not STOP.is_set():
            try:
                processed = self.run_once()
            except PyMongoError as error:
                LOGGER.warning("MongoDB no disponible para Outbox: %s", type(error).__name__)
                processed = False
            if not processed:
                STOP.wait(settings.outbox_poll_seconds)


def _stop(_signum, _frame):
    STOP.set()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    start_http_server(settings.outbox_metrics_port)
    collection = get_client()[settings.mongodb_database].outbox
    worker = OutboxWorker(
        collection,
        get_redis_client(),
        Neo4jGraphService(get_neo4j_client()),
    )
    LOGGER.info("worker=%s iniciado", worker.worker_id)
    try:
        worker.run_forever()
    finally:
        close_redis_client()
        close_neo4j_client()
        close_client()


if __name__ == "__main__":
    main()
