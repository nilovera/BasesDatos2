import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from pymongo.errors import DuplicateKeyError

from backend.app.errors import DomainError
from backend.app.match_listing import match_listing
from backend.app.repository import MongoRepository


class MatchNavigationTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.repo = MongoRepository(self.client)
        self.db = self.repo.db

    def test_selected_teams_determine_rosters(self):
        self.db.partidos.find_one.return_value = {"equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"}}
        self.db.equipos.count_documents.return_value = 2
        self.db.jugadores.find.return_value.sort.return_value = []
        result = self.repo.simulation_context("PAR-0001", ["EQ-03", "EQ-04"])
        self.assertEqual(("EQ-03", "EQ-04"), (result["localId"], result["visitanteId"]))
        self.assertEqual(["EQ-03", "EQ-04"], self.db.jugadores.find.call_args.args[0]["equipoId"]["$in"])

    def test_same_or_incomplete_teams_cannot_create_a_match(self):
        self.db.partidos.find_one.return_value = {"equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"}}
        for pair in (["EQ-01", "EQ-01"], ["EQ-01", None]):
            with self.assertRaises(DomainError) as error:
                self.repo.simulation_context("PAR-0001", pair)
            self.assertEqual(400, error.exception.status)
        self.db.jugadores.find.assert_not_called()

    def test_missing_team_is_rejected(self):
        self.db.partidos.find_one.return_value = {"equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"}}
        self.db.equipos.count_documents.return_value = 1
        with self.assertRaises(DomainError) as error:
            self.repo.simulation_context("PAR-0001", ["EQ-01", "EQ-99"])
        self.assertEqual("TEAM_NOT_FOUND", error.exception.code)

    def test_new_match_keeps_its_selected_rivals_and_does_not_reset_base(self):
        self.db.contadores.find_one_and_update.return_value = {"valor": 8}
        self.db.partidos.find_one.return_value = {"equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"}}
        session = self.client.start_session.return_value.__enter__.return_value
        session.with_transaction.side_effect = lambda callback, **kwargs: callback(session)
        self.repo.get_simulation = MagicMock(return_value={"estado": "LISTA"})
        self.repo.create_simulation("PAR-0001", 2030, 25, [], {}, {"localId": "EQ-03", "visitanteId": "EQ-04"})
        match = self.db.partidos.insert_one.call_args.args[0]
        self.assertEqual({"localId": "EQ-03", "visitanteId": "EQ-04"}, match["equipos"])
        self.assertEqual("PAR-1007", match["partidoId"])
        self.assertEqual("LISTA", self.db.simulaciones.insert_one.call_args.args[0]["estado"])
        self.db.partidos.update_one.assert_not_called()

    def test_simultaneous_start_conflict_leaves_second_match_unstarted(self):
        self.db.simulaciones.find_one.return_value = {"estado": "LISTA"}
        self.db.simulaciones.find_one_and_update.side_effect = DuplicateKeyError("another match is running")
        with self.assertRaises(DomainError) as error:
            self.repo.control_simulation("SIM-second", "INICIAR")
        self.assertEqual(409, error.exception.status)
        self.assertEqual("SIMULATION_ALREADY_RUNNING", error.exception.code)

    def test_finished_match_cannot_be_restarted(self):
        self.db.simulaciones.find_one.return_value = {"estado": "FINALIZADA"}
        with self.assertRaises(DomainError) as error:
            self.repo.control_simulation("SIM-finished", "INICIAR")
        self.assertEqual(409, error.exception.status)
        self.db.simulaciones.find_one_and_update.assert_not_called()

    def test_upcoming_listing_has_teams_and_pagination_without_future_plan(self):
        now = datetime.now(timezone.utc)
        rows = [{"simulacionId": f"SIM-{i}", "partidoId": f"PAR-{1000+i}", "estado": "LISTA",
                 "segundoPartido": 0, "creadoEn": now, "plan": [{"tipo": "GOL"}]} for i in range(3)]
        cursor = self.db.simulaciones.find.return_value
        cursor.sort.return_value.skip.return_value.limit.return_value = rows
        self.db.partidos.find.return_value = [
            {"partidoId": row["partidoId"], "equipos": {"localId": "EQ-03", "visitanteId": "EQ-04"},
             "marcador": {"local": 0, "visitante": 0}} for row in rows]
        self.db.equipos.find.return_value.sort.return_value = [
            {"equipoId": "EQ-03", "nombre": "Brasil"}, {"equipoId": "EQ-04", "nombre": "Uruguay"}]
        self.db.simulaciones.count_documents.return_value = 0
        result = match_listing(self.db, limit=2)
        self.assertTrue(result["hayMas"])
        self.assertEqual(2, len(result["items"]))
        self.assertEqual(["Brasil", "Uruguay"], [t["nombre"] for t in result["items"][0]["equipos"]])
        self.assertNotIn("plan", result["items"][0])
        self.assertEqual({"estado": {"$in": ["LISTA"]}}, self.db.simulaciones.find.call_args.args[0])
        self.db.simulaciones.insert_one.assert_not_called()

    def test_history_is_paginated_newest_first(self):
        cursor = self.db.simulaciones.find.return_value
        cursor.sort.return_value.skip.return_value.limit.return_value = []
        self.db.partidos.find.return_value = []
        self.db.equipos.find.return_value.sort.return_value = []
        match_listing(self.db, "finalizados", page=2)
        cursor.sort.assert_called_once_with([("creadoEn", -1), ("simulacionId", -1)])
        cursor.sort.return_value.skip.assert_called_once_with(24)

    def test_invalid_listing_group_is_rejected(self):
        with self.assertRaises(DomainError):
            match_listing(self.db, "todos-con-plan")
        self.db.simulaciones.find.assert_not_called()


if __name__ == "__main__":
    unittest.main()
