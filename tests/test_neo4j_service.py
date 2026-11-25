import unittest

from backend.app.errors import DomainError
from backend.app.neo4j_service import Neo4jGraphService


class FakeNeo4jClient:
    def __init__(self):
        self.players = {"JUG-0001"}
        self.teams = {"EQ-01", "EQ-33"}

    def health(self):
        return "UP"

    def query_one(self, query, parameters=None):
        parameters = parameters or {}
        if "count(e) AS equipos" in query:
            return {
                "equipos": 64,
                "jugadores": 1024,
                "partidos": 1,
                "confederaciones": 6,
                "relaciones": 1097,
            }
        if "origenExiste" in query:
            return {
                "origenExiste": parameters["origin_id"] in self.teams,
                "destinoExiste": parameters["destination_id"] in self.teams,
            }
        if "shortestPath" in query:
            return {
                "nodos": [
                    {"tipo": "Equipo", "id": "EQ-01", "nombre": "Argentina"},
                    {"tipo": "Confederacion", "id": "CONMEBOL", "nombre": "CONMEBOL"},
                    {"tipo": "Torneo", "id": "TOR-2030", "nombre": "Fixture 2030"},
                    {"tipo": "Confederacion", "id": "CONCACAF", "nombre": "CONCACAF"},
                    {"tipo": "Equipo", "id": "EQ-33", "nombre": "México"},
                ],
                "relaciones": ["MIEMBRO_DE", "PARTICIPA_EN", "PARTICIPA_EN", "MIEMBRO_DE"],
                "saltos": 4,
            }
        if "MATCH (j:Jugador" in query:
            player_id = parameters["player_id"]
            return {"id": player_id, "nombre": "Jugador"} if player_id in self.players else None
        if "MATCH (e:Equipo" in query:
            team_id = parameters["team_id"]
            return {"id": team_id, "nombre": "Equipo"} if team_id in self.teams else None
        return None

    def query_all(self, query, parameters=None):
        if "candidato:Jugador" in query:
            return [
                {
                    "jugadorId": "JUG-0017",
                    "nombre": "Recomendado",
                    "posicion": "Arquero",
                    "equipoId": "EQ-02",
                    "equipo": "Bolivia",
                    "diferenciaRanking": 1,
                    "criterio": "CONMEBOL",
                }
            ]
        if "rival:Equipo" in query:
            return [
                {
                    "partidoId": "PAR-0001",
                    "equipoId": "EQ-33",
                    "nombre": "México",
                    "inicioProgramado": "2030-06-13T20:00:00Z",
                }
            ]
        return []


class Neo4jGraphServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = Neo4jGraphService(FakeNeo4jClient())

    def test_summary_exposes_reference_counts(self):
        self.assertEqual(1097, self.service.summary()["relaciones"])

    def test_rivals_traverse_a_shared_match(self):
        result = self.service.rivals("EQ-01")
        self.assertEqual("EQ-33", result["items"][0]["equipoId"])

    def test_recommendation_excludes_source_and_returns_criterion(self):
        result = self.service.recommendations("JUG-0001", 10)
        self.assertEqual("MISMA_POSICION_Y_CONFEDERACION", result["criterio"])
        self.assertNotEqual("JUG-0001", result["items"][0]["jugadorId"])

    def test_team_path_is_multihop_and_explainable(self):
        result = self.service.team_path("EQ-01", "EQ-33")
        self.assertEqual(4, result["saltos"])
        self.assertEqual("EQ-01", result["nodos"][0]["id"])
        self.assertEqual("EQ-33", result["nodos"][-1]["id"])

    def test_missing_team_is_rejected(self):
        with self.assertRaises(DomainError) as context:
            self.service.rivals("EQ-99")
        self.assertEqual(404, context.exception.status)


if __name__ == "__main__":
    unittest.main()
