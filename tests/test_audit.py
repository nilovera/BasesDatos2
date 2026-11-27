import base64
import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import UUID

from pymongo.errors import PyMongoError

from backend.app.audit_context import audit_scope, current_context, make_audit_event, request_dependencies, require_audit_admin
from backend.app.audit_service import CassandraAuditService
from backend.app.audit_worker import AuditRelay
from backend.app.cassandra_service import CassandraCommentService
from backend.app.errors import DomainError
from backend.app.repository import MongoRepository


class FakeBatch:
    def __init__(self, **kwargs):
        self.statements = []

    def add(self, statement, params):
        self.statements.append((statement, params))


class MemoryCassandra:
    """Doble del driver, no una prueba de Cassandra ni de su replicacion."""
    def __init__(self):
        self.operations = {}
        self.actor_view = {}
        self.resource_view = {}
        self.requests = {}
        self.comments = {}
        self.locators = {}
        self.fail_batch = False

    def prepare(self, statement):
        return " ".join(statement.split())

    def execute(self, statement, params=None):
        if isinstance(statement, FakeBatch):
            if self.fail_batch:
                self.fail_batch = False
                raise OSError("simulated Cassandra timeout")
            for query, args in statement.statements:
                if query.startswith("INSERT INTO audit_by_actor_day"):
                    self.actor_view[args[:4]] = args[-1]
                elif query.startswith("INSERT INTO audit_by_resource_day"):
                    self.resource_view[args[:5]] = args[-1]
                elif query.startswith("UPDATE audit_operations"):
                    self.operations[args[0]]["projected"] = True
                elif query.startswith("INSERT INTO comments_by_match"):
                    self.comments[args[4]] = dict(content=args[6], status=args[7])
                elif query.startswith("INSERT INTO comment_locator"):
                    self.locators[args[0]] = SimpleNamespace(
                        match_id=args[1], match_bucket=args[2], match_shard=args[3],
                        user_id=args[4], day_bucket=args[5], created_at=args[6], comment_id=args[0])
                elif query.startswith("UPDATE comments_by_match"):
                    self.comments[args[-1]]["status"] = args[0]
            return []
        query = " ".join(statement.split())
        if query.startswith("INSERT INTO audit_operations"):
            key, payload = params
            if key not in self.operations:
                self.operations[key] = dict(event_json=payload, projected=False)
                row = SimpleNamespace(applied=True)
            else:
                row = SimpleNamespace(applied=False, **self.operations[key])
            return SimpleNamespace(one=lambda: row)
        if query.startswith("INSERT INTO comment_write_requests"):
            key, payload_hash, comment_id, created_at = params
            if key not in self.requests:
                self.requests[key] = dict(payload_hash=payload_hash, comment_id=comment_id, created_at=created_at)
                row = SimpleNamespace(applied=True)
            else:
                row = SimpleNamespace(applied=False, **self.requests[key])
            return SimpleNamespace(one=lambda: row)
        if query.startswith("SELECT * FROM comment_locator"):
            row = self.locators.get(params[0])
            return SimpleNamespace(one=lambda: row)
        if query.startswith("SELECT content, status FROM comments_by_match"):
            value = self.comments.get(params[-1])
            row = SimpleNamespace(**value) if value else None
            return SimpleNamespace(one=lambda: row)
        if "FROM audit_by_" in query:
            actor = "FROM audit_by_actor_day" in query
            view, count = (self.actor_view, 2) if actor else (self.resource_view, 3)
            rows = [(key, data) for key, data in view.items() if key[:count] == params[:count]]
            if "occurred_at = %s" in query:
                rows = [(k, d) for k, d in rows if k[count] == params[count] and k[count+1].int > params[count+1].int]
            elif "occurred_at < %s" in query:
                rows = [(k, d) for k, d in rows if k[count] < params[count]]
            rows.sort(key=lambda x: (-x[0][count].timestamp(), x[0][count+1].int))
            return [SimpleNamespace(event_json=d) for k, d in rows[:params[-1]]]
        raise AssertionError("Unexpected CQL: " + query)


class AuditTests(unittest.TestCase):
    def setUp(self):
        driver = ModuleType("cassandra")
        driver.ConsistencyLevel = SimpleNamespace(LOCAL_ONE=1)
        query = ModuleType("cassandra.query")
        query.BatchStatement, query.BatchType = FakeBatch, SimpleNamespace(LOGGED=1)
        self.modules = patch.dict(sys.modules, {"cassandra": driver, "cassandra.query": query})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.session = MemoryCassandra()
        self.audit = CassandraAuditService(self.session)
        self.comments = CassandraCommentService(self.session)
        self.now = datetime(2030, 6, 13, 12, 30, 0, 123456, tzinfo=timezone.utc)

    def event(self, number=1, **kwargs):
        with audit_scope("USR-0001", "SESION_LAB", request_id="request-001", role="ADMIN"):
            return make_audit_event("REGISTRAR_EVENTO", "EVENTO", "EVE-000001",
                                    operation_id="op:" + str(number), occurred_at=self.now, **kwargs)

    def test_no_identity_leaks_between_requests(self):
        with audit_scope("USR-0001", "SESION_LAB", role="ADMIN"):
            self.assertEqual("USR-0001", current_context()["actorId"])
        self.assertEqual("SERVICIO", current_context()["actorTipo"])

    def test_declared_author_is_distinguished_from_verified_lab_session(self):
        with audit_scope("anonimo", "ANONIMO"):
            event = make_audit_event("PUBLICAR_COMENTARIO", "COMENTARIO", "c", declared_actor="USR-0003")
        self.assertEqual(("USR-0003", "DECLARADO"), (event["actorId"], event["actorTipo"]))
        with audit_scope("simulador", "SERVICIO"):
            event = make_audit_event("PUBLICAR_COMENTARIO", "COMENTARIO", "c", declared_actor="USR-0003")
        self.assertEqual("simulador", event["actorId"])

    def test_session_cannot_claim_another_comment_author(self):
        with audit_scope("USR-0001", "SESION_LAB"):
            with self.assertRaises(DomainError) as caught:
                self.comments.publish("PAR-0001", "USR-0002", "text", "idem-key-00000001")
        self.assertEqual(403, caught.exception.status)
        self.assertFalse(self.session.comments)

    def test_details_cannot_include_tokens_passwords_or_bodies(self):
        for key in ("token", "password", "contenido", "body", "sesionId"):
            with self.assertRaises(ValueError):
                self.event(detail={key: "not-to-be-stored"})

    def test_audit_queries_require_an_admin_lab_session(self):
        for actor_type, role in (("ANONIMO", None), ("DECLARADO", "ADMIN"), ("SESION_LAB", "FAN")):
            with audit_scope("USR-0001", actor_type, role=role):
                with self.assertRaises(DomainError):
                    require_audit_admin()
        with audit_scope("USR-0001", "SESION_LAB", role="ADMIN"):
            require_audit_admin()

    def test_replay_preserves_one_event_and_original_request(self):
        event = self.event()
        self.audit.store(event)
        retry = {**event, "requestId": "another-request", "fecha": "2030-06-14T00:00:00Z"}
        self.audit.store(retry)
        self.assertEqual(1, len(self.session.actor_view))
        saved = self.audit.by_actor("USR-0001", "20300613")["items"][0]
        self.assertEqual("request-001", saved["requestId"])
        self.assertEqual(event["fecha"], saved["fecha"])

    def test_same_operation_with_different_effect_is_conflict(self):
        event = self.event()
        self.audit.store(event)
        with self.assertRaises(DomainError) as caught:
            self.audit.store({**event, "accion": "CORREGIR_EVENTO"})
        self.assertEqual(409, caught.exception.status)

    def test_failed_projection_retries_without_losing_original_event(self):
        self.session.fail_batch = True
        with self.assertRaises(OSError):
            self.audit.store(self.event())
        self.assertFalse(self.session.actor_view)
        self.audit.store(self.event())
        self.assertEqual(1, len(self.session.actor_view))
        self.assertEqual(1, len(self.session.resource_view))

    def test_pagination_does_not_skip_events_at_same_millisecond(self):
        for number in range(9):
            self.audit.store(self.event(number))
        ids, cursor = [], None
        while True:
            page = self.audit.by_actor("USR-0001", "20300613", cursor, 2)
            ids.extend(e["auditoriaId"] for e in page["items"])
            cursor = page["siguienteCursor"]
            if not cursor:
                break
        self.assertEqual(9, len(ids))
        self.assertEqual(9, len(set(ids)))

    def test_cursor_cannot_be_reused_for_another_actor_or_day(self):
        for n in (1, 2):
            self.audit.store(self.event(n))
        cursor = self.audit.by_actor("USR-0001", "20300613", limit=1)["siguienteCursor"]
        for actor, day in (("USR-0002", "20300613"), ("USR-0001", "20300614")):
            with self.assertRaises(DomainError):
                self.audit.by_actor(actor, day, cursor)

    def test_malformed_cursor_and_impossible_day_are_rejected(self):
        for data in (None, [], "text", {"v": 1}):
            cursor = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
            with self.assertRaises(DomainError):
                self.audit.by_actor("USR-0001", "20300613", cursor)
        with self.assertRaises(DomainError):
            self.audit.by_actor("USR-0001", "20300230")

    def test_resource_query_returns_only_its_partition(self):
        self.audit.store(self.event())
        self.assertEqual(1, len(self.audit.by_resource("EVENTO", "EVE-000001", "20300613")["items"]))
        self.assertFalse(self.audit.by_resource("EVENTO", "EVE-000002", "20300613")["items"])

    def test_comment_replay_has_one_audit_without_comment_text(self):
        with audit_scope("anonimo", "ANONIMO"):
            first = self.comments.publish("PAR-0001", "USR-0001", "private-content", "key-comment-00001")
            again = self.comments.publish("PAR-0001", "USR-0001", "private-content", "key-comment-00001")
        self.assertEqual(first["comentarioId"], again["comentarioId"])
        self.assertEqual(1, len(self.session.actor_view))
        self.assertNotIn("private-content", next(iter(self.session.actor_view.values())))

    def test_comment_batch_failure_does_not_publish_audit_and_retry_completes(self):
        with audit_scope("anonimo", "ANONIMO"):
            self.session.fail_batch = True
            with self.assertRaises(DomainError):
                self.comments.publish("PAR-0001", "USR-0001", "text", "key-comment-00001")
            self.assertFalse(self.session.actor_view)
            self.comments.publish("PAR-0001", "USR-0001", "text", "key-comment-00001")
        self.assertEqual(1, len(self.session.actor_view))

    def test_moderations_keep_history_and_old_replay_does_not_revert_new_status(self):
        with audit_scope("anonimo", "ANONIMO"):
            comment = self.comments.publish("PAR-0001", "USR-0001", "text", "key-comment-00001")
            cid = comment["comentarioId"]
            self.comments.moderate(cid, "OCULTO", "USR-0002", "first reason", "moderation-key-001")
            self.comments.moderate(cid, "VISIBLE", "USR-0002", "second reason", "moderation-key-002")
            self.comments.moderate(cid, "OCULTO", "USR-0002", "first reason", "moderation-key-001")
        self.assertEqual("VISIBLE", self.session.comments[UUID(cid)]["status"])
        self.assertEqual(3, len(self.session.resource_view))
        data = self.audit.by_actor("USR-0002", datetime.now(timezone.utc).strftime("%Y%m%d"))["items"]
        self.assertEqual(2, len(data))
        self.assertEqual({"OCULTO", "VISIBLE"}, {e["detalle"]["estado"] for e in data})

    def test_technical_log_dependency_mapping(self):
        self.assertEqual(["mongodb", "influxdb"], request_dependencies("/api/v1/partidos/{partidoId}/telemetria/posiciones", "POST"))
        self.assertEqual(["cassandra"], request_dependencies("/api/v1/auditoria/actores/{actorId}", "GET"))


class AuditRelayTests(unittest.TestCase):
    def setUp(self):
        self.collection, self.service = MagicMock(), MagicMock()
        self.doc = {"_id": "op:1", "evento": {"operacionId": "op:1"}, "intentos": 2}
        self.collection.find_one_and_update.return_value = self.doc
        self.relay = AuditRelay(self.collection, lambda: self.service)

    def test_pending_is_removed_only_after_cassandra_accepts(self):
        calls = []
        self.service.store.side_effect = lambda e: calls.append("store")
        self.collection.delete_one.side_effect = lambda q: calls.append("delete")
        self.relay.run_once()
        self.assertEqual(["store", "delete"], calls)

    def test_cassandra_failure_keeps_durable_pending_and_schedules_retry(self):
        self.service.store.side_effect = OSError("down")
        with self.assertLogs("uvicorn.error", level="WARNING") as logs:
            self.relay.run_once()
        self.assertIn("operacionId=op:1", logs.output[0])
        self.assertNotIn("down", logs.output[0])
        self.collection.delete_one.assert_not_called()
        update = self.collection.update_one.call_args.args[1]
        self.assertEqual("PENDIENTE", update["$set"]["estado"])
        self.assertIn("proximoIntentoEn", update["$set"])
        self.assertNotIn("down", json.dumps(update, default=str))

    def test_claim_can_recover_an_expired_lease(self):
        self.relay.run_once()
        conditions = self.collection.find_one_and_update.call_args.args[0]["$or"]
        self.assertIn("bloqueoHasta", conditions[1])


class MongoAuditTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.repo = MongoRepository(self.client)
        self.db = self.repo.db
        self.session = self.client.start_session.return_value.__enter__.return_value
        self.session.with_transaction.side_effect = lambda callback, **kwargs: callback(self.session)

    def test_create_simulation_enqueues_in_same_transaction(self):
        self.db.contadores.find_one_and_update.return_value = {"valor": 1}
        self.db.partidos.find_one.return_value = {"equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"}}
        self.repo.get_simulation = MagicMock(return_value={})
        self.repo.create_simulation("PAR-0001", 2030, 30, [], {})
        kwargs = self.db.auditoria_pendiente.insert_one.call_args.kwargs
        self.assertIs(self.session, kwargs["session"])
        event = self.db.auditoria_pendiente.insert_one.call_args.args[0]["evento"]
        self.assertEqual("CREAR_SIMULACION", event["accion"])

    def test_control_simulation_cannot_confirm_without_durable_audit(self):
        self.db.simulaciones.find_one.return_value = {"estado": "LISTA"}
        self.db.simulaciones.find_one_and_update.return_value = {
            "partidoId": "PAR-1000", "estado": "EJECUTANDO", "velocidad": 30}
        self.db.auditoria_pendiente.insert_one.side_effect = PyMongoError("queue unavailable")
        with self.assertRaises(DomainError) as caught:
            self.repo.control_simulation("SIM-test", "INICIAR")
        self.assertEqual(503, caught.exception.status)
        self.assertIs(self.session, self.db.simulaciones.find_one_and_update.call_args.kwargs["session"])

    def test_event_replay_does_not_enqueue_second_audit(self):
        self.db.eventos_oficiales.find_one.return_value = {"already": "stored"}
        self.repo._replay_or_conflict = MagicMock(return_value="replayed")
        self.assertEqual("replayed", self.repo.register_event("PAR-0001", "key", {"tipo": "GOL"}, datetime.now(timezone.utc)))
        self.db.auditoria_pendiente.insert_one.assert_not_called()

    def _event_fixture(self):
        match = {"partidoId": "PAR-0001", "estado": "EN_CURSO", "version": 2,
                 "ultimaSecuencia": 1, "equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"},
                 "marcador": {"local": 0, "visitante": 0}}
        self.db.partidos.find_one.return_value = match
        self.db.contadores.find_one_and_update.return_value = {"valor": 3}
        self.db.partidos.update_one.return_value.modified_count = 1
        self.repo._player_teams = MagicMock(return_value={})
        updated = {**match, "version": 3, "ultimaSecuencia": 2, "marcador": {"local": 1, "visitante": 0}}
        return updated

    def test_official_event_and_audit_share_transaction_and_actor(self):
        updated = self._event_fixture()
        self.db.eventos_oficiales.find_one.return_value = None
        with patch("backend.app.repository.apply_event", return_value=updated):
            with audit_scope("USR-0001", "SESION_LAB", request_id="request-gol", role="ADMIN"):
                result = self.repo.register_event("PAR-0001", "event-key", {"tipo": "GOL"}, datetime.now(timezone.utc))
        call = self.db.auditoria_pendiente.insert_one.call_args
        self.assertIs(self.session, call.kwargs["session"])
        event = call.args[0]["evento"]
        self.assertEqual(result.body["eventoId"], event["recursoId"])
        self.assertEqual(("USR-0001", "request-gol", "REGISTRAR_EVENTO"),
                         (event["actorId"], event["requestId"], event["accion"]))
        self.assertIs(self.session, self.db.eventos_oficiales.insert_one.call_args.kwargs["session"])

    def test_correction_audit_references_original_event(self):
        updated = self._event_fixture()
        self.db.eventos_oficiales.find_one.side_effect = [None,
            {"eventoId": "EVE-000001", "tipo": "GOL", "datos": {}}, None]
        with patch("backend.app.repository.apply_event", return_value=updated):
            self.repo.register_event("PAR-0001", "correction-key",
                {"tipo": "CORRECCION_EVENTO", "eventoOriginalId": "EVE-000001"}, datetime.now(timezone.utc))
        event = self.db.auditoria_pendiente.insert_one.call_args.args[0]["evento"]
        self.assertEqual("CORREGIR_EVENTO", event["accion"])
        self.assertEqual("EVE-000001", event["detalle"]["eventoOriginalId"])
        self.assertEqual("EVE-000001", event["recursoId"])
        self.assertEqual("EVE-000003", event["detalle"]["eventoId"])


class AuditContractTests(unittest.TestCase):
    def test_queries_are_documented_without_history_mutation_endpoints(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        spec = json.loads((root / "backend/openapi.json").read_text(encoding="utf-8"))
        routes = {k: v for k, v in spec["paths"].items() if k.startswith("/api/v1/auditoria")}
        self.assertEqual(3, len(routes))
        for route in routes.values():
            self.assertEqual({"get"}, set(route))
            self.assertIn("403", route["get"]["responses"])
            self.assertIn("X-Session-ID", {p["name"] for p in route["get"]["parameters"]})
        params = spec["paths"]["/api/v1/comentarios/{comentarioId}/moderacion"]["patch"]["parameters"]
        self.assertIn("Idempotency-Key", {p["name"] for p in params})


if __name__ == "__main__":
    unittest.main()
