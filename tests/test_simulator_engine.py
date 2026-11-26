import json
import unittest
from datetime import datetime, timezone

from backend.app.domain import apply_event
from backend.app.simulator_engine import (
    MATCH_SECONDS,
    active_players,
    ball_sample,
    build_plan,
    event_comment,
    position_samples,
    select_lineup,
)


def roster(team, offset):
    positions = ["ARQUERO", "ARQUERO"] + ["DEFENSOR"] * 6 + ["MEDIOCAMPISTA"] * 5 + ["DELANTERO"] * 3
    return [
        {"jugadorId": f"JUG-{offset + index:04d}", "equipoId": team, "nombre": f"Jugador {index}", "posicion": position}
        for index, position in enumerate(positions, 1)
    ]


class SimulatorEngineTests(unittest.TestCase):
    def setUp(self):
        self.local = "EQ-01"
        self.visitor = "EQ-33"
        self.rosters = {self.local: roster(self.local, 0), self.visitor: roster(self.visitor, 512)}
        self.start = datetime(2030, 6, 13, 20, 0, tzinfo=timezone.utc)

    def test_seed_reproduces_complete_match_plan(self):
        first = build_plan(2030, self.local, self.visitor, self.rosters, self.start)
        second = build_plan(2030, self.local, self.visitor, self.rosters, self.start)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        self.assertEqual("INICIO_PARTIDO", first[0]["tipo"])
        self.assertEqual("FIN_PARTIDO", first[-1]["tipo"])
        self.assertEqual(MATCH_SECONDS, first[-1]["segundo"])
        self.assertEqual(1, sum(event["tipo"] == "GOL_ANULADO_VAR" for event in first))
        self.assertEqual(6, sum(event["tipo"] == "SUSTITUCION" for event in first))
        self.assertGreaterEqual(sum(event["tipo"] == "GOL" for event in first), 2)
        local_starters, local_bench = select_lineup(self.rosters[self.local])
        visitor_starters, visitor_bench = select_lineup(self.rosters[self.visitor])
        starters = {self.local: local_starters, self.visitor: visitor_starters}
        benches = {self.local: local_bench, self.visitor: visitor_bench}
        for event in first:
            if event["tipo"] in {"GOL", "GOL_ANULADO_VAR", "TARJETA"}:
                active_ids = {
                    player["jugadorId"]
                    for player in active_players(starters, benches, first, event["equipoId"], event["segundo"])
                }
                self.assertIn(event["jugadorId"], active_ids)

    def test_every_planned_event_has_a_comment(self):
        plan = build_plan(2030, self.local, self.visitor, self.rosters, self.start)
        for event in plan:
            self.assertTrue(event_comment(event))

    def test_lineup_is_442_with_five_reserves(self):
        starters, bench = select_lineup(self.rosters[self.local])
        counts = {position: sum(player["posicion"] == position for player in starters) for position in {p["posicion"] for p in starters}}
        self.assertEqual({"ARQUERO": 1, "DEFENSOR": 4, "MEDIOCAMPISTA": 4, "DELANTERO": 2}, counts)
        self.assertEqual(5, len(bench))

    def test_players_stay_in_bounds_and_ball_matches_goal_area(self):
        plan = build_plan(2030, self.local, self.visitor, self.rosters, self.start)
        local_starters, local_bench = select_lineup(self.rosters[self.local])
        visitor_starters, visitor_bench = select_lineup(self.rosters[self.visitor])
        starters = {self.local: local_starters, self.visitor: visitor_starters}
        benches = {self.local: local_bench, self.visitor: visitor_bench}
        goal = next(event for event in plan if event["tipo"] == "GOL")
        positions, possession = position_samples(
            2030, goal["segundo"], self.local, self.visitor, starters, benches, plan,
            self.start,
        )
        self.assertEqual(22, len(positions))
        self.assertTrue(all(0 <= row["x"] <= 100 and 0 <= row["y"] <= 100 for row in positions))
        ball = ball_sample(2030, goal["segundo"], possession, positions, plan, self.start)
        self.assertEqual(goal["x"], ball["x"])
        self.assertEqual(goal["y"], ball["y"])
        self.assertEqual(goal["equipoId"], possession)
        scorer = next(row for row in positions if row["jugadorId"] == goal["jugadorId"])
        self.assertEqual((goal["x"], goal["y"]), (scorer["x"], scorer["y"]))

    def test_var_does_not_change_score_and_final_closes_match(self):
        match = {
            "estado": "EN_CURSO", "equipos": {"localId": self.local, "visitanteId": self.visitor},
            "marcador": {"local": 1, "visitante": 0}, "ultimaSecuencia": 4, "version": 5,
        }
        player = self.rosters[self.local][-1]
        var = {
            "tipo": "GOL_ANULADO_VAR", "equipoId": self.local, "jugadorId": player["jugadorId"],
            "periodo": 2, "minuto": 70, "motivo": "OFFSIDE", "x": 93, "y": 50,
            "ocurridoEn": self.start,
        }
        updated = apply_event(match, var, {player["jugadorId"]: self.local})
        self.assertEqual(match["marcador"], updated["marcador"])
        finished = apply_event(updated, {"tipo": "FIN_PARTIDO", "periodo": 2, "minuto": 90, "ocurridoEn": self.start})
        self.assertEqual("FINALIZADO", finished["estado"])


if __name__ == "__main__":
    unittest.main()
