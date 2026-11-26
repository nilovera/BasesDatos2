import asyncio
from contextlib import ExitStack
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from pymongo.errors import OperationFailure

from backend.app.cleanup_simulations import apply_update_cleanup, cleanup_history, restore_history
from backend.app.metrics import HTTP_IN_FLIGHT, application_request
from backend.app.mongo_monitoring import MongoMonitoringCollector


class MonitoringUpdateTests(unittest.TestCase):
    def test_concurrency_tracks_overlapping_requests_and_returns_to_zero(self):
        initial = HTTP_IN_FLIGHT._value.get()
        with ExitStack() as requests:
            for _ in range(3):
                requests.enter_context(application_request("/api/v1/directo"))
            self.assertEqual(initial + 3, HTTP_IN_FLIGHT._value.get())
        self.assertEqual(initial, HTTP_IN_FLIGHT._value.get())
        with self.assertRaises(asyncio.CancelledError):
            with application_request("/api/v1/directo"):
                raise asyncio.CancelledError()
        self.assertEqual(initial, HTTP_IN_FLIGHT._value.get())

    def test_monitoring_requests_do_not_count_as_application_concurrency(self):
        initial = HTTP_IN_FLIGHT._value.get()
        for path in ("/metrics", "/health", "/directo/assets/app.js"):
            with application_request(path):
                self.assertEqual(initial, HTTP_IN_FLIGHT._value.get())

    def test_mongo_collector_uses_real_status_and_dbstats_without_documents(self):
        client = MagicMock()
        client.admin.command.return_value = {"connections": {"current": 7}, "opcounters": {"query": 123}}
        client.get_database.return_value.command.return_value = {"dataSize": 800, "storageSize": 1600, "indexSize": 200}
        collector = MongoMonitoringCollector(lambda: client, "fixture2030")
        samples = {sample.name: sample.value for family in collector.collect() for sample in family.samples}
        self.assertEqual(7, samples["fixture2030_mongodb_connections"])
        self.assertEqual(123, samples["fixture2030_mongodb_operations_total"])
        self.assertEqual(800, samples["fixture2030_mongodb_data_bytes"])
        self.assertEqual(1600, samples["fixture2030_mongodb_storage_bytes"])
        self.assertEqual(1, samples["fixture2030_mongodb_metrics_up"])
        client.get_database.return_value.partidos.find.assert_not_called()

    def test_mongo_failure_does_not_publish_false_zero_connection_values(self):
        client = MagicMock()
        client.admin.command.side_effect = OperationFailure("monitoring permission unavailable")
        samples = {sample.name: sample.value for family in MongoMonitoringCollector(lambda: client, "db").collect() for sample in family.samples}
        self.assertEqual({"fixture2030_mongodb_metrics_up": 0}, samples)

    def test_collector_registration_does_not_connect_to_the_database(self):
        factory = MagicMock()
        list(MongoMonitoringCollector(factory, "db").describe())
        factory.assert_not_called()


class HistoryCleanupTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.db = self.client.get_database.return_value
        self.db.simulaciones.find.return_value = [{"_id": "SIM-old"}]
        self.session = self.client.start_session.return_value.__enter__.return_value
        self.session.with_transaction.side_effect = lambda callback, **kwargs: callback(self.session)
        self.cutoff = datetime(2026, 11, 26, tzinfo=timezone.utc)

    def test_preview_is_read_only_and_only_targets_inactive_simulations(self):
        result = cleanup_history(self.client, self.cutoff)
        self.assertFalse(result["aplicado"])
        self.assertEqual(1, result["candidatas"])
        query = self.db.simulaciones.find.call_args.args[0]
        self.assertEqual(["LISTA", "FINALIZADA", "ERROR"], query["estado"]["$in"])
        self.db.create_collection.assert_not_called()
        self.db.simulaciones.delete_one.assert_not_called()

    def test_reapplying_update_does_not_delete_new_simulations(self):
        self.db.mantenimientos.find_one_and_update.return_value = {
            "_id": "limpieza-incremento-14", "completada": True, "loteId": "LIM-previous",
        }
        result = apply_update_cleanup(self.client, self.cutoff)
        self.assertFalse(result["aplicado"])
        self.db.simulaciones.find.assert_not_called()
        self.db.simulaciones.delete_one.assert_not_called()

    def test_cleanup_backs_up_exact_document_in_same_transaction_before_deletion(self):
        original = {"_id": "SIM-old", "estado": "FINALIZADA", "plan": [{"tipo": "GOL"}]}
        self.db.simulaciones.find_one.return_value = original
        self.db.simulaciones.delete_one.return_value.deleted_count = 1
        result = cleanup_history(self.client, self.cutoff, True)
        self.assertEqual(["SIM-old"], result["eliminadas"])
        backup = self.db.__getitem__.return_value.insert_one.call_args
        self.assertEqual(original, backup.args[0]["simulacion"])
        self.assertIs(backup.kwargs["session"], self.db.simulaciones.delete_one.call_args.kwargs["session"])
        self.db.partidos.delete_many.assert_not_called()
        self.db.equipos.delete_many.assert_not_called()
        self.db.jugadores.delete_many.assert_not_called()

    def test_failed_backup_never_deletes_the_simulation(self):
        self.db.simulaciones.find_one.return_value = {"_id": "SIM-old", "estado": "FINALIZADA"}
        self.db.__getitem__.return_value.insert_one.side_effect = OperationFailure("backup failed")
        with self.assertRaises(OperationFailure):
            cleanup_history(self.client, self.cutoff, True)
        self.db.simulaciones.delete_one.assert_not_called()

    def test_concurrently_started_match_is_preserved(self):
        self.db.simulaciones.find_one.return_value = None
        result = cleanup_history(self.client, self.cutoff, True)
        self.assertEqual([], result["eliminadas"])
        self.assertEqual(["SIM-old"], result["preservadasPorCambioDeEstado"])
        self.db.simulaciones.delete_one.assert_not_called()

    def test_restore_is_idempotent_and_does_not_overwrite_existing_simulation(self):
        batch = "LIM-" + "0" * 36
        self.db.__getitem__.return_value.find.return_value = [{"simulacion": {"_id": "SIM-old", "estado": "FINALIZADA"}}]
        self.db.simulaciones.update_one.return_value.upserted_id = None
        result = restore_history(self.client, batch)
        self.assertEqual(0, result["restauradas"])
        self.assertIn("$setOnInsert", self.db.simulaciones.update_one.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
