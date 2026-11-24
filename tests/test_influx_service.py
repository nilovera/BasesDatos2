import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.errors import DomainError  # noqa: E402
from app.influx_service import (  # noqa: E402
    InfluxTelemetryService,
    decode_position_cursor,
    encode_position_cursor,
)


class FakeInfluxClient:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.writes = []
        self.queries = []

    def health(self):
        return "UP"

    def write_lines(self, database, lines):
        self.writes.append((database, list(lines)))

    def query(self, database, sql):
        self.queries.append((database, sql))
        return list(self.rows)


def position(player, team, captured_at, x=10.0, y=20.0):
    return SimpleNamespace(
        jugador_id=player,
        equipo_id=team,
        capturado_en=captured_at,
        x=x,
        y=y,
        periodo=1,
        segundo_partido=10,
    )


class InfluxTelemetryServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeInfluxClient()
        self.service = InfluxTelemetryService(
            self.client, "fixture2030-detalle", "fixture2030-historico"
        )
        self.time = datetime(2030, 6, 13, 20, 0, 10, tzinfo=timezone.utc)

    def test_position_cursor_round_trip_uses_time_and_player(self):
        cursor = encode_position_cursor(self.time, "JUG-0001")
        captured_at, player = decode_position_cursor(cursor)
        self.assertEqual(self.time, captured_at)
        self.assertEqual("JUG-0001", player)

    def test_invalid_position_cursor_is_rejected(self):
        with self.assertRaises(DomainError) as context:
            decode_position_cursor("not-a-valid-cursor")
        self.assertEqual("INVALID_TELEMETRY_CURSOR", context.exception.code)

    def test_same_timestamp_for_different_players_is_valid(self):
        result = self.service.write_positions(
            "PAR-0001",
            [
                position("JUG-0001", "EQ-01", self.time),
                position("JUG-0513", "EQ-33", self.time),
            ],
        )
        self.assertEqual(2, result["muestrasAceptadas"])
        database, lines = self.client.writes[0]
        self.assertEqual("fixture2030-detalle", database)
        self.assertIn("equipo_id=EQ-01,jugador_id=JUG-0001", lines[0])
        self.assertIn("equipo_id=EQ-33,jugador_id=JUG-0513", lines[1])

    def test_duplicate_player_and_timestamp_in_batch_is_rejected(self):
        sample = position("JUG-0001", "EQ-01", self.time)
        with self.assertRaises(DomainError) as context:
            self.service.write_positions("PAR-0001", [sample, sample])
        self.assertEqual("DUPLICATE_TELEMETRY_SAMPLE", context.exception.code)
        self.assertEqual([], self.client.writes)

    def test_page_cursor_does_not_skip_shared_timestamps(self):
        self.client.rows = [
            {"time": "2030-06-13T20:00:10Z", "equipo_id": "EQ-01", "jugador_id": "JUG-0001", "x": 1, "y": 2, "periodo": 1, "segundo_partido": 10},
            {"time": "2030-06-13T20:00:10Z", "equipo_id": "EQ-33", "jugador_id": "JUG-0513", "x": 3, "y": 4, "periodo": 1, "segundo_partido": 10},
            {"time": "2030-06-13T20:00:20Z", "equipo_id": "EQ-01", "jugador_id": "JUG-0001", "x": 5, "y": 6, "periodo": 1, "segundo_partido": 20},
        ]
        page = self.service.list_positions("PAR-0001", limit=2)
        self.assertEqual(2, len(page["items"]))
        captured_at, player = decode_position_cursor(page["siguienteCursor"])
        self.assertEqual("JUG-0513", player)
        self.assertEqual(10, captured_at.second)
        self.assertIn("ORDER BY time, jugador_id", self.client.queries[0][1])

    def test_heatmap_clamps_boundary_to_last_cell(self):
        self.client.rows = [{"x": 100, "y": 100}, {"x": 0, "y": 0}]
        result = self.service.heatmap("PAR-0001", "JUG-0001", 10)
        coordinates = {(item["celdaX"], item["celdaY"]) for item in result["celdas"]}
        self.assertEqual({(0, 0), (9, 9)}, coordinates)

    def test_aggregation_writes_to_historical_database(self):
        self.client.rows = [
            {
                "ventana": "2030-06-13T20:00:00Z",
                "equipo_id": "EQ-01",
                "posesion_promedio": 51.25,
                "pases_total": 210,
                "tiros_finales": 3,
                "goles_finales": 1,
                "muestras": 90,
            }
        ]
        result = self.service.aggregate_team_statistics("PAR-0001")
        self.assertEqual(1, result["resumenesGenerados"])
        database, lines = self.client.writes[0]
        self.assertEqual("fixture2030-historico", database)
        self.assertIn("resumen_equipo_15m,partido_id=PAR-0001,equipo_id=EQ-01", lines[0])


if __name__ == "__main__":
    unittest.main()
