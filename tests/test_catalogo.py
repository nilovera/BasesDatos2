"""Controles de integridad para evitar inconsistencias entre las futuras semillas."""

import copy
import json
import unittest

from scripts.catalogo import SOURCE, generate, validate


class CatalogIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = generate(json.loads(SOURCE.read_text(encoding="utf-8")))

    def setUp(self):
        self.data = copy.deepcopy(self.catalog)

    def test_valid_reference_dataset(self):
        validate(self.data)
        self.assertEqual(self.data["equipos"][0]["nombre"], "Argentina")
        self.assertEqual(self.data["equipos"][32]["nombre"], "México")

    def test_duplicate_player_is_rejected(self):
        self.data["jugadores"][1]["_id"] = self.data["jugadores"][0]["_id"]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            validate(self.data)

    def test_orphan_player_is_rejected(self):
        self.data["jugadores"][0]["equipo_id"] = "EQ-99"
        with self.assertRaisesRegex(ValueError, "huérfano"):
            validate(self.data)

    def test_external_code_must_resolve_to_an_existing_team(self):
        self.data["equivalencias_codigos"]["ARG"] = "EQ-99"
        with self.assertRaisesRegex(ValueError, "Equivalencia"):
            validate(self.data)

    def test_match_cannot_play_against_itself(self):
        self.data["partidos"][0]["equipo_visitante_id"] = "EQ-01"
        with self.assertRaisesRegex(ValueError, "Participantes"):
            validate(self.data)

    def test_naive_timestamp_is_rejected(self):
        self.data["partidos"][0]["inicio_programado"] = "2030-06-13T20:00:00"
        with self.assertRaisesRegex(ValueError, "UTC"):
            validate(self.data)

    def test_unsupported_state_is_rejected(self):
        self.data["partidos"][0]["estado"] = "EnCurso"
        with self.assertRaisesRegex(ValueError, "Estado"):
            validate(self.data)

    def test_event_requires_an_existing_match(self):
        self.data["eventos"] = [{"_id": "EVE-000001", "partido_id": "PAR-9999"}]
        with self.assertRaisesRegex(ValueError, "inexistente"):
            validate(self.data)


if __name__ == "__main__":
    unittest.main()
