import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from backend.app.outbox_worker import OutboxWorker, PROJECT_EVENT_LUA


class FakeCollection:
    def __init__(self, message=None, oldest=None):
        self.message = message
        self.oldest = oldest
        self.claim_filter = None
        self.claim_update = None
        self.updates = []

    def find_one_and_update(self, query, update, **_kwargs):
        self.claim_filter = query
        self.claim_update = update
        return self.message

    def update_one(self, query, update):
        self.updates.append((query, update))
        return SimpleNamespace(modified_count=1)

    def count_documents(self, query):
        state = query.get("estado")
        return 1 if self.oldest and isinstance(state, dict) and state.get("$in") else 0

    def find_one(self, *_args, **_kwargs):
        return self.oldest


class FakeRedis:
    def __init__(self, result=1):
        self.result = result
        self.calls = []

    def eval(self, *args):
        self.calls.append(args)
        return self.result


class FakeGraph:
    def __init__(self):
        self.messages = []

    def project_official_event(self, value):
        self.messages.append(value)


def message(attempts=1):
    return {
        "_id": "OUT-1",
        "outboxId": "OUT-1",
        "eventoId": "EVE-000001",
        "partidoId": "PAR-0001",
        "tipo": "GOL",
        "secuencia": 1,
        "payload": {"resultado": {"versionPartido": 2}},
        "intentos": attempts,
        "creadoEn": datetime.now(timezone.utc),
    }


class OutboxWorkerTests(unittest.TestCase):
    def test_claim_accepts_pending_and_expired_leases(self):
        collection = FakeCollection(message())
        worker = OutboxWorker(collection, FakeRedis(), worker_id="worker-test")

        claimed = worker.claim()

        self.assertEqual("OUT-1", claimed["outboxId"])
        states = collection.claim_filter["$or"]
        self.assertEqual("PENDIENTE", states[0]["estado"])
        self.assertEqual("PROCESANDO", states[1]["estado"])
        self.assertEqual(1, collection.claim_update["$inc"]["intentos"])
        self.assertEqual("worker-test", collection.claim_update["$set"]["bloqueo"]["workerId"])

    def test_projection_is_atomic_and_deduplicated_by_event(self):
        redis = FakeRedis(result=1)
        worker = OutboxWorker(FakeCollection(), redis, worker_id="worker-test")

        inserted = worker.project(message())

        self.assertEqual(1, inserted)
        args = redis.calls[0]
        self.assertIn("HEXISTS", args[0])
        self.assertIn("XADD", args[0])
        self.assertIn("HSET", PROJECT_EVENT_LUA)
        self.assertEqual("outbox:procesados", args[2])
        self.assertEqual("marcador:partido:PAR-0001", args[5])
        self.assertEqual("EVE-000001", args[6])

    def test_replay_does_not_create_a_second_projection(self):
        worker = OutboxWorker(FakeCollection(), FakeRedis(result=0), worker_id="worker-test")
        self.assertEqual(0, worker.project(message()))

    def test_graph_projection_uses_same_idempotent_event(self):
        graph = FakeGraph()
        worker = OutboxWorker(FakeCollection(), FakeRedis(), graph, worker_id="worker-test")
        worker.project_graph(message())
        self.assertEqual("EVE-000001", graph.messages[0]["eventoId"])

    def test_complete_marks_message_published_and_releases_lease(self):
        collection = FakeCollection()
        worker = OutboxWorker(collection, FakeRedis(), worker_id="worker-test")

        worker.complete(message())

        query, update = collection.updates[0]
        self.assertEqual("worker-test", query["bloqueo.workerId"])
        self.assertEqual("PUBLICADO", update["$set"]["estado"])
        self.assertIn("expiraEn", update["$set"])
        self.assertIn("bloqueo", update["$unset"])

    @patch("backend.app.outbox_worker.random.uniform", return_value=0)
    def test_transient_failure_returns_to_pending_with_backoff(self, _uniform):
        collection = FakeCollection()
        worker = OutboxWorker(collection, FakeRedis(), worker_id="worker-test")

        worker.fail(message(attempts=2), RuntimeError("redis down"))

        _, update = collection.updates[0]
        self.assertEqual("PENDIENTE", update["$set"]["estado"])
        self.assertIsNotNone(update["$set"]["proximoIntentoEn"])
        self.assertIn("RuntimeError", update["$set"]["ultimoError"])

    def test_exhausted_message_moves_to_failed(self):
        collection = FakeCollection()
        worker = OutboxWorker(collection, FakeRedis(), worker_id="worker-test")

        worker.fail(message(attempts=8), RuntimeError("permanent"))

        _, update = collection.updates[0]
        self.assertEqual("FALLIDO", update["$set"]["estado"])
        self.assertIsNone(update["$set"]["proximoIntentoEn"])

    def test_refresh_metrics_accepts_naive_mongodb_datetime(self):
        collection = FakeCollection(oldest={"creadoEn": datetime.now()})
        worker = OutboxWorker(collection, FakeRedis(), worker_id="worker-test")

        worker.refresh_metrics()


if __name__ == "__main__":
    unittest.main()
