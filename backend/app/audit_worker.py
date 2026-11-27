"""Reenvio durable MongoDB -> Cassandra; el historial final vive en Cassandra."""
import logging
import threading
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from pymongo import ReturnDocument

LOGGER = logging.getLogger("uvicorn.error")


class AuditRelay:
    def __init__(self, collection, service_factory):
        self.collection = collection
        self.service_factory = service_factory
        self.worker_id = str(uuid4())

    def run_once(self):
        now = datetime.now(timezone.utc)
        doc = self.collection.find_one_and_update(
            {"$or": [{"estado": "PENDIENTE", "proximoIntentoEn": {"$lte": now}},
                      {"estado": "ENVIANDO", "bloqueoHasta": {"$lte": now}}]},
            {"$set": {"estado": "ENVIANDO", "workerId": self.worker_id,
                      "bloqueoHasta": now + timedelta(seconds=30)}, "$inc": {"intentos": 1}},
            sort=[("creadoEn", 1), ("_id", 1)], return_document=ReturnDocument.AFTER)
        if doc is None:
            return False
        ownership = {"_id": doc["_id"], "workerId": self.worker_id, "estado": "ENVIANDO"}
        try:
            self.service_factory().store(doc["evento"])
            # Un crash antes del delete provoca un replay seguro, no otro evento.
            self.collection.delete_one(ownership)
        except Exception as error:
            delay = min(60, 2 ** min(6, int(doc["intentos"])))
            self.collection.update_one(ownership, {
                "$set": {"estado": "PENDIENTE", "proximoIntentoEn": now + timedelta(seconds=delay),
                          "ultimoErrorTipo": type(error).__name__},
                "$unset": {"workerId": "", "bloqueoHasta": ""}})
            LOGGER.warning("audit_delivery_pending operacionId=%s errorTipo=%s", doc["_id"], type(error).__name__)
        return True


_stop = threading.Event()
_thread = None


def start_audit_worker():
    global _thread
    from .audit_service import CassandraAuditService
    from .cassandra_client import get_cassandra_session
    from .config import settings
    from .database import get_client
    if _thread and _thread.is_alive():
        return
    _stop.clear()

    def loop():
        relay = AuditRelay(get_client()[settings.mongodb_database].auditoria_pendiente,
                           lambda: CassandraAuditService(get_cassandra_session()))
        while not _stop.is_set():
            try:
                relay.run_once()
            except Exception as error:
                LOGGER.warning("audit_relay_unavailable errorTipo=%s", type(error).__name__)
            _stop.wait(0.5)

    _thread = threading.Thread(target=loop, name="fixture2030-audit", daemon=True)
    _thread.start()


def stop_audit_worker():
    if _thread:
        _stop.set()
        _thread.join(timeout=10)
