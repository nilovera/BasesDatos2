"""Motor determinista de un partido de 90 minutos.

No conoce bases de datos ni reloj de pared. La misma semilla, planteles y segundo
de partido producen siempre el mismo plan y las mismas coordenadas.
"""

import hashlib
import math
import random
from datetime import datetime, timedelta, timezone


MATCH_SECONDS = 90 * 60
TELEMETRY_STEP_SECONDS = 5

FORMATION = {
    "ARQUERO": [(7, 50)],
    "DEFENSOR": [(25, 15), (21, 38), (21, 62), (25, 85)],
    "MEDIOCAMPISTA": [(46, 18), (42, 40), (42, 60), (46, 82)],
    "DELANTERO": [(68, 35), (72, 65)],
}

COMMENT_TEMPLATES = (
    "El equipo intenta salir jugando desde el fondo.",
    "La presión en mitad de cancha no afloja.",
    "Buen cambio de frente para encontrar espacio.",
    "La tribuna acompaña cada avance.",
    "Partido intenso y muy disputado.",
    "El bloque defensivo vuelve a ordenarse.",
    "Gran recuperación cerca del círculo central.",
    "Se prepara un nuevo ataque por la banda.",
)


def _rng(seed, *parts):
    material = ":".join(str(value) for value in (seed, *parts)).encode("utf-8")
    number = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    return random.Random(number)


def select_lineup(players):
    """Elige 1-4-4-2 y cinco suplentes de forma estable."""
    by_position = {}
    for player in sorted(players, key=lambda item: item["jugadorId"]):
        by_position.setdefault(player["posicion"], []).append(player)
    starters = (
        by_position["ARQUERO"][:1]
        + by_position["DEFENSOR"][:4]
        + by_position["MEDIOCAMPISTA"][:4]
        + by_position["DELANTERO"][:2]
    )
    starter_ids = {item["jugadorId"] for item in starters}
    bench = [item for item in sorted(players, key=lambda row: row["jugadorId"]) if item["jugadorId"] not in starter_ids][:5]
    if len(starters) != 11 or len(bench) < 3:
        raise ValueError("Cada equipo necesita once titulares y al menos tres suplentes")
    return starters, bench


def build_plan(seed, local_team, visitor_team, rosters, start_time=None):
    """Construye hechos coherentes y ordenados; siempre incluye VAR y final."""
    start_time = start_time or datetime.now(timezone.utc)
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    rng = random.Random(seed)
    local_starters, local_bench = select_lineup(rosters[local_team])
    visitor_starters, visitor_bench = select_lineup(rosters[visitor_team])
    starters = {local_team: local_starters, visitor_team: visitor_starters}
    benches = {local_team: local_bench, visitor_team: visitor_bench}

    substitution_events = []
    for team_index, team in enumerate((local_team, visitor_team)):
        substitution_seconds = (58 * 60 + team_index * 90, 70 * 60 + team_index * 75, 81 * 60 + team_index * 45)
        substitution_positions = ("DELANTERO", "MEDIOCAMPISTA", "DEFENSOR")
        for index, second in enumerate(substitution_seconds):
            position = substitution_positions[index]
            leaving = next(player for player in reversed(starters[team]) if player["posicion"] == position)
            entering = next(player for player in benches[team] if player["posicion"] == position)
            substitution_events.append({
                "segundo": second, "tipo": "SUSTITUCION", "equipoId": team,
                "saleJugadorId": leaving["jugadorId"], "entraJugadorId": entering["jugadorId"],
            })

    def available(team, second):
        active = list(starters[team])
        player_by_id = {player["jugadorId"]: player for player in starters[team] + benches[team]}
        for substitution in substitution_events:
            if substitution["equipoId"] == team and substitution["segundo"] <= second:
                active = [
                    player_by_id[substitution["entraJugadorId"]]
                    if player["jugadorId"] == substitution["saleJugadorId"] else player
                    for player in active
                ]
        return active

    plan = [{"segundo": 0, "tipo": "INICIO_PARTIDO"}]
    goal_seconds = sorted(rng.sample(range(8 * 60, 84 * 60, TELEMETRY_STEP_SECONDS), rng.randint(2, 4)))
    for second in goal_seconds:
        team = rng.choice([local_team, visitor_team])
        active = available(team, second)
        attackers = [p for p in active if p["posicion"] in {"DELANTERO", "MEDIOCAMPISTA"}]
        scorer = rng.choice(attackers)
        assistants = [p for p in active if p["jugadorId"] != scorer["jugadorId"]]
        assistant = rng.choice(assistants) if rng.random() < 0.8 else None
        is_local = team == local_team
        plan.append({
            "segundo": second,
            "tipo": "GOL",
            "equipoId": team,
            "jugadorId": scorer["jugadorId"],
            "asistenteJugadorId": assistant["jugadorId"] if assistant else None,
            "x": round(rng.uniform(88, 96) if is_local else rng.uniform(4, 12), 2),
            "y": round(rng.uniform(34, 66), 2),
        })

    var_second = rng.choice([value for value in range(18 * 60, 78 * 60, TELEMETRY_STEP_SECONDS) if all(abs(value - goal) > 120 for goal in goal_seconds)])
    var_team = rng.choice([local_team, visitor_team])
    var_player = rng.choice([p for p in available(var_team, var_second) if p["posicion"] == "DELANTERO"])
    plan.append({
        "segundo": var_second,
        "tipo": "GOL_ANULADO_VAR",
        "equipoId": var_team,
        "jugadorId": var_player["jugadorId"],
        "motivo": rng.choice(["OFFSIDE", "FALTA_PREVIA", "MANO"]),
        "x": 93.0 if var_team == local_team else 7.0,
        "y": round(rng.uniform(36, 64), 2),
    })

    card_seconds = sorted(rng.sample(range(12 * 60, 86 * 60), 5))
    for index, second in enumerate(card_seconds):
        team = [local_team, visitor_team][index % 2]
        candidates = [p for p in available(team, second) if p["posicion"] != "ARQUERO"]
        player = rng.choice(candidates)
        plan.append({
            "segundo": second,
            "tipo": "TARJETA",
            "equipoId": team,
            "jugadorId": player["jugadorId"],
            "color": "ROJA" if index == 4 and rng.random() < 0.25 else "AMARILLA",
            "motivo": rng.choice(["Falta táctica", "Entrada temeraria", "Protesta reiterada"]),
        })

    plan.extend(substitution_events)

    plan.append({"segundo": MATCH_SECONDS, "tipo": "FIN_PARTIDO"})
    plan.sort(key=lambda event: (event["segundo"], event["tipo"]))
    for index, event in enumerate(plan):
        second = event["segundo"]
        event["indice"] = index
        event["periodo"] = 1 if second < 45 * 60 else 2
        event["minuto"] = min(90, second // 60)
        event["ocurridoEn"] = (start_time + timedelta(seconds=second)).isoformat().replace("+00:00", "Z")
    return plan


def active_players(starters, benches, plan, team_id, second):
    active = [dict(player) for player in starters[team_id]]
    by_id = {item["jugadorId"]: dict(item) for item in starters[team_id] + benches[team_id]}
    for event in plan:
        if event["segundo"] > second:
            break
        if event["tipo"] == "SUSTITUCION" and event["equipoId"] == team_id:
            active = [by_id[event["entraJugadorId"]] if p["jugadorId"] == event["saleJugadorId"] else p for p in active]
    return active


def possession_team(seed, second, local_team, visitor_team):
    block = second // 35
    return local_team if _rng(seed, "possession", block).random() < 0.54 else visitor_team


def position_samples(seed, second, local_team, visitor_team, starters, benches, plan, captured_at):
    official_action = next(
        (
            event
            for event in plan
            if event["segundo"] == second
            and event["tipo"] in {"GOL", "GOL_ANULADO_VAR"}
        ),
        None,
    )
    possession = (
        official_action["equipoId"]
        if official_action
        else possession_team(seed, second, local_team, visitor_team)
    )
    samples = []
    for team in (local_team, visitor_team):
        players = active_players(starters, benches, plan, team, second)
        slots = {key: list(value) for key, value in FORMATION.items()}
        for player in players:
            base_x, base_y = slots[player["posicion"]].pop(0)
            if team == visitor_team:
                base_x = 100 - base_x
            advance = 7 if team == possession else -3
            if team == visitor_team:
                advance *= -1
            movement = _rng(seed, "movement", player["jugadorId"])
            phase_x = movement.uniform(0, math.tau)
            phase_y = movement.uniform(0, math.tau)
            pace_x = movement.uniform(18.0, 32.0)
            pace_y = movement.uniform(14.0, 27.0)
            x_offset = math.sin(second / pace_x + phase_x) * 3.2
            x_offset += math.sin(second / 8.0 + phase_y) * 0.8
            y_offset = math.sin(second / pace_y + phase_y) * 4.5
            y_offset += math.sin(second / 9.0 + phase_x) * 1.0
            x = max(1, min(99, base_x + advance + x_offset))
            y = max(2, min(98, base_y + y_offset))
            samples.append({
                "equipoId": team,
                "jugadorId": player["jugadorId"],
                "x": round(x, 3),
                "y": round(y, 3),
                "periodo": 1 if second < 2700 else 2,
                "segundoPartido": second,
                "capturadoEn": captured_at,
            })

    # En una definición oficial el autor y la pelota deben compartir la zona.
    # Así el evento y la telemetría cuentan la misma jugada reproducible.
    if official_action:
        for sample in samples:
            if sample["jugadorId"] == official_action["jugadorId"]:
                sample["x"] = official_action["x"]
                sample["y"] = official_action["y"]
            elif sample["jugadorId"] == official_action.get("asistenteJugadorId"):
                direction = -1 if official_action["equipoId"] == local_team else 1
                sample["x"] = max(0, min(100, official_action["x"] + direction * 4))
                sample["y"] = max(0, min(100, official_action["y"] + 3))
    return samples, possession


def ball_sample(seed, second, possession, player_samples, plan, captured_at):
    close_event = next((event for event in plan if event["tipo"] in {"GOL", "GOL_ANULADO_VAR"} and abs(event["segundo"] - second) <= TELEMETRY_STEP_SECONDS), None)
    if close_event:
        x, y = close_event["x"], close_event["y"]
        event_id = f"plan-{close_event['indice']:03d}"
    else:
        candidates = [item for item in player_samples if item["equipoId"] == possession]
        carrier = _rng(seed, "ball", second // 15).choice(candidates)
        phase = _rng(seed, "ball-offset").uniform(0, math.tau)
        x = max(0, min(100, carrier["x"] + math.sin(second / 3.0 + phase) * 1.5))
        y = max(0, min(100, carrier["y"] + math.cos(second / 3.5 + phase) * 1.5))
        event_id = None
    return {
        "x": round(x, 3), "y": round(y, 3),
        "periodo": 1 if second < 2700 else 2,
        "segundoPartido": second, "equipoPosesionId": possession,
        "eventoId": event_id, "capturadoEn": captured_at,
    }


def event_comment(event):
    event_type = event["tipo"]
    if event_type == "INICIO_PARTIDO":
        return "¡Comenzó el partido!"
    if event_type == "GOL":
        return f"¡GOL al minuto {event['minuto']}! La jugada terminó dentro del área."
    if event_type == "GOL_ANULADO_VAR":
        return f"El VAR anuló el gol por {event['motivo']}."
    if event_type == "TARJETA":
        return f"Tarjeta {event['color'].lower()} al minuto {event['minuto']}."
    if event_type == "SUSTITUCION":
        return f"Cambio confirmado al minuto {event['minuto']}."
    if event_type == "FIN_PARTIDO":
        return "Final del partido. Se cierra la transmisión."
    raise ValueError(f"Tipo de evento sin comentario: {event_type}")

