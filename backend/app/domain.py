import copy
import hashlib
import json

from .errors import DomainError


def canonical_request_hash(method, path, partido_id, body):
    canonical = json.dumps(
        {
            "method": method.upper(),
            "path": path,
            "partidoId": partido_id,
            "body": body,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _match_teams(match):
    return {match["equipos"]["localId"], match["equipos"]["visitanteId"]}


def _validate_goal(match, event, player_teams):
    team_id = event["equipoId"]
    player_id = event["jugadorId"]
    if team_id not in _match_teams(match):
        raise DomainError(422, "TEAM_NOT_IN_MATCH", "El equipo no participa del partido")
    if player_teams.get(player_id) != team_id:
        raise DomainError(
            422,
            "PLAYER_NOT_IN_TEAM",
            "El jugador no pertenece al equipo informado",
            {"jugadorId": player_id, "equipoId": team_id},
        )
    assistant = event.get("asistenteJugadorId")
    if assistant:
        if assistant == player_id:
            raise DomainError(422, "INVALID_ASSIST", "El goleador no puede asistirse a si mismo")
        if player_teams.get(assistant) != team_id:
            raise DomainError(422, "PLAYER_NOT_IN_TEAM", "El asistente no pertenece al equipo informado")


def _validate_player_event(match, event, player_teams):
    if event["equipoId"] not in _match_teams(match):
        raise DomainError(422, "TEAM_NOT_IN_MATCH", "El equipo no participa del partido")
    if player_teams.get(event["jugadorId"]) != event["equipoId"]:
        raise DomainError(422, "PLAYER_NOT_IN_TEAM", "El jugador no pertenece al equipo informado")


def _validate_substitution(match, event, player_teams):
    team_id = event["equipoId"]
    leaving = event["saleJugadorId"]
    entering = event["entraJugadorId"]
    if team_id not in _match_teams(match):
        raise DomainError(422, "TEAM_NOT_IN_MATCH", "El equipo no participa del partido")
    if leaving == entering:
        raise DomainError(
            422,
            "INVALID_SUBSTITUTION",
            "El jugador que sale y el que entra deben ser distintos",
        )
    if player_teams.get(leaving) != team_id or player_teams.get(entering) != team_id:
        raise DomainError(
            422,
            "PLAYER_NOT_IN_TEAM",
            "Ambos jugadores deben pertenecer al equipo informado",
        )


def _change_goal(score, match, team_id, delta):
    side = "local" if team_id == match["equipos"]["localId"] else "visitante"
    next_value = score[side] + delta
    if next_value < 0:
        raise DomainError(
            409,
            "INVALID_CORRECTION",
            "La corrección produciría un marcador negativo",
        )
    score[side] = next_value


def apply_event(match, event, player_teams=None, original_event=None):
    """Aplica reglas puras y devuelve una copia actualizada del agregado."""
    player_teams = player_teams or {}
    updated = copy.deepcopy(match)
    event_type = event["tipo"]

    if event_type == "INICIO_PARTIDO":
        if match["estado"] != "PROGRAMADO":
            raise DomainError(409, "INVALID_MATCH_STATE", "El partido no está programado")
        updated["estado"] = "EN_CURSO"
        updated["inicioReal"] = event["ocurridoEn"]

    elif event_type == "GOL":
        if match["estado"] != "EN_CURSO":
            raise DomainError(409, "INVALID_MATCH_STATE", "El partido no está en curso")
        _validate_goal(match, event, player_teams)
        _change_goal(updated["marcador"], match, event["equipoId"], 1)

    elif event_type == "SUSTITUCION":
        if match["estado"] != "EN_CURSO":
            raise DomainError(409, "INVALID_MATCH_STATE", "El partido no está en curso")
        _validate_substitution(match, event, player_teams)

    elif event_type in {"TARJETA", "GOL_ANULADO_VAR"}:
        if match["estado"] != "EN_CURSO":
            raise DomainError(409, "INVALID_MATCH_STATE", "El partido no está en curso")
        _validate_player_event(match, event, player_teams)

    elif event_type == "FIN_PARTIDO":
        if match["estado"] != "EN_CURSO":
            raise DomainError(409, "INVALID_MATCH_STATE", "El partido no está en curso")
        updated["estado"] = "FINALIZADO"
        updated["finReal"] = event["ocurridoEn"]

    elif event_type == "CORRECCION_EVENTO":
        if original_event is None:
            raise DomainError(404, "EVENT_NOT_FOUND", "El evento original no existe")
        if original_event["tipo"] not in {"GOL", "SUSTITUCION"}:
            raise DomainError(
                422,
                "EVENT_NOT_CORRECTABLE",
                "Solo se corrigen goles o sustituciones en este incremento",
            )
        replacement = event["reemplazo"]
        if original_event["tipo"] == "GOL":
            _change_goal(
                updated["marcador"], match, original_event["equipoId"], -1
            )
        if replacement["tipo"] == "GOL":
            _validate_goal(match, replacement, player_teams)
            _change_goal(updated["marcador"], match, replacement["equipoId"], 1)
        else:
            _validate_substitution(match, replacement, player_teams)

    else:
        raise DomainError(422, "UNSUPPORTED_EVENT", "Tipo de evento no soportado")

    updated["ultimaSecuencia"] = int(match["ultimaSecuencia"]) + 1
    updated["version"] = int(match["version"]) + 1
    return updated
