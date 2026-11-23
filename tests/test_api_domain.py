import unittest

from backend.app.domain import apply_event, canonical_request_hash
from backend.app.errors import DomainError


def base_match(state="PROGRAMADO", home=0, away=0, sequence=0, version=1):
    return {
        "partidoId": "PAR-0001",
        "equipos": {"localId": "EQ-01", "visitanteId": "EQ-33"},
        "estado": state,
        "marcador": {"local": home, "visitante": away},
        "ultimaSecuencia": sequence,
        "version": version,
    }


class ApiDomainTests(unittest.TestCase):
    def test_request_hash_is_stable_for_json_key_order(self):
        first = canonical_request_hash("POST", "/events", "PAR-0001", {"b": 2, "a": 1})
        second = canonical_request_hash("post", "/events", "PAR-0001", {"a": 1, "b": 2})
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))

    def test_request_hash_changes_with_body(self):
        first = canonical_request_hash("POST", "/events", "PAR-0001", {"a": 1})
        second = canonical_request_hash("POST", "/events", "PAR-0001", {"a": 2})
        self.assertNotEqual(first, second)

    def test_start_transitions_match_and_increments_version(self):
        result = apply_event(
            base_match(),
            {"tipo": "INICIO_PARTIDO", "ocurridoEn": "2030-06-13T20:00:00Z"},
        )
        self.assertEqual("EN_CURSO", result["estado"])
        self.assertEqual(1, result["ultimaSecuencia"])
        self.assertEqual(2, result["version"])

    def test_start_is_rejected_when_match_is_already_running(self):
        with self.assertRaises(DomainError) as context:
            apply_event(
                base_match("EN_CURSO"),
                {"tipo": "INICIO_PARTIDO", "ocurridoEn": "2030-06-13T20:00:00Z"},
            )
        self.assertEqual("INVALID_MATCH_STATE", context.exception.code)

    def test_goal_updates_home_score(self):
        result = apply_event(
            base_match("EN_CURSO", sequence=1, version=2),
            {"tipo": "GOL", "equipoId": "EQ-01", "jugadorId": "JUG-0013"},
            {"JUG-0013": "EQ-01"},
        )
        self.assertEqual({"local": 1, "visitante": 0}, result["marcador"])
        self.assertEqual(2, result["ultimaSecuencia"])

    def test_goal_rejects_player_from_another_team(self):
        with self.assertRaises(DomainError) as context:
            apply_event(
                base_match("EN_CURSO"),
                {"tipo": "GOL", "equipoId": "EQ-01", "jugadorId": "JUG-0513"},
                {"JUG-0513": "EQ-33"},
            )
        self.assertEqual("PLAYER_NOT_IN_TEAM", context.exception.code)

    def test_correction_replaces_goal_without_double_counting(self):
        result = apply_event(
            base_match("EN_CURSO", home=1, sequence=2, version=3),
            {
                "tipo": "CORRECCION_EVENTO",
                "reemplazo": {
                    "tipo": "GOL",
                    "equipoId": "EQ-01",
                    "jugadorId": "JUG-0014",
                },
            },
            {"JUG-0014": "EQ-01"},
            {"tipo": "GOL", "equipoId": "EQ-01", "jugadorId": "JUG-0013"},
        )
        self.assertEqual({"local": 1, "visitante": 0}, result["marcador"])
        self.assertEqual(4, result["version"])

    def test_substitution_requires_distinct_players(self):
        with self.assertRaises(DomainError) as context:
            apply_event(
                base_match("EN_CURSO"),
                {
                    "tipo": "SUSTITUCION",
                    "equipoId": "EQ-01",
                    "saleJugadorId": "JUG-0009",
                    "entraJugadorId": "JUG-0009",
                },
                {"JUG-0009": "EQ-01"},
            )
        self.assertEqual("INVALID_SUBSTITUTION", context.exception.code)


if __name__ == "__main__":
    unittest.main()
