import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from backend.app.errors import DomainError
from backend.app.live_service import live_score, simulation_document, telemetry_queries, transmission, transmission_comments


class LiveViewTests(unittest.TestCase):
    def test_stale_redis_projection_does_not_undo_a_goal(self):
        match = {"ultimaSecuencia": 8, "marcador": {"local": 1, "visitante": 2}}
        self.assertEqual(match["marcador"], live_score(match, {"ultimaSecuencia": "7", "local": "0", "visitante": "2"}))
        self.assertEqual(match["marcador"], live_score(match, {}))
        self.assertEqual(match["marcador"], live_score(match, {"ultimaSecuencia": "8", "local": "1", "visitante": "2"}))

    def test_no_match_returns_not_found_without_creating_one(self):
        db = MagicMock()
        db.simulaciones.find_one.return_value = None
        with self.assertRaises(DomainError) as error:
            simulation_document(db, None)
        self.assertEqual(404, error.exception.status)
        db.simulaciones.insert_one.assert_not_called()

    def test_invalid_identifiers_cannot_be_interpolated_into_sql(self):
        for args in (("PAR-1004' OR 1=1",), ("PAR-1004", "x'"), ("PAR-1004", None, "EQ-01'")):
            with self.assertRaises(DomainError):
                telemetry_queries(*args)

    def test_heatmap_filters_team_and_player_without_truncating_raw_history(self):
        positions, ball, heatmap = telemetry_queries("PAR-1004", "JUG-0001", "EQ-01")
        self.assertIn("MAX(segundo_partido)", positions)
        self.assertIn("LIMIT 22", positions)
        self.assertIn("ORDER BY time DESC LIMIT 1", ball)
        self.assertIn("jugador_id = 'JUG-0001'", heatmap)
        self.assertIn("equipo_id = 'EQ-01'", heatmap)
        self.assertIn("COUNT(*)", heatmap)
        self.assertIn("GROUP BY cx, cy LIMIT 240", heatmap)

    def test_public_snapshot_never_exposes_the_future_plan(self):
        repo = MagicMock()
        redis = MagicMock()
        doc = {"partidoId": "PAR-1004", "plan": [{"tipo": "GOL", "minuto": 85}]}
        repo.db.simulaciones.find_one.return_value = doc
        repo.db.partidos.find_one.return_value = {"equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"}, "ultimaSecuencia": 1, "marcador": {"local": 0, "visitante": 0}}
        repo.db.equipos.find.return_value = []
        repo.db.jugadores.find.return_value = []
        repo._simulation_response.return_value = {"estado": "EJECUTANDO"}
        repo.list_events.return_value = {"items": [{"tipo": "INICIO_PARTIDO"}]}
        redis.hgetall.return_value = {}
        snapshot = transmission(repo, redis)
        self.assertNotIn("plan", snapshot)
        self.assertEqual([{"tipo": "INICIO_PARTIDO"}], snapshot["eventos"])
        self.assertEqual({"local": 0, "visitante": 0}, snapshot["marcador"])

    def test_finished_match_keeps_comments_from_its_final_time(self):
        db = MagicMock()
        service = MagicMock()
        db.simulaciones.find_one.return_value = {
            "partidoId": "PAR-1004", "estado": "FINALIZADA",
            "actualizadoEn": datetime(2026, 11, 26, 20, 1, 13),
        }
        comment = {"comentarioId": "one", "creadoEn": datetime(2026, 11, 26, 20, 1, tzinfo=timezone.utc)}
        service.list_by_match.return_value = {"items": [comment]}
        result = transmission_comments(db, "SIM-89dae14d-664c-4d51-9140-009be092ef9b", service)
        self.assertEqual([comment], result["items"])
        self.assertEqual(["202611262001", "202611262000", "202611261959"], [call.args[1] for call in service.list_by_match.call_args_list])


if __name__ == "__main__":
    unittest.main()
