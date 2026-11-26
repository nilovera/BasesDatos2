"""Lecturas de transmisión con dependencias explícitas; no requiere FastAPI para los tests."""

from datetime import datetime, timedelta, timezone
import re

from .errors import DomainError


def simulation_document(db, simulation_id):
    if simulation_id and not re.fullmatch(r"SIM-[0-9a-f-]{36}", simulation_id):
        raise DomainError(400, "INVALID_SIMULATION_ID", "Simulación inválida")
    if simulation_id:
        document = db.simulaciones.find_one({"_id": simulation_id})
    else:
        document = db.simulaciones.find_one(
            {"estado": {"$in": ["EJECUTANDO", "PAUSADA"]}}, sort=[("creadoEn", -1)]
        ) or db.simulaciones.find_one({}, sort=[("creadoEn", -1)])
    if document is None:
        raise DomainError(404, "SIMULATION_NOT_FOUND", "Todavía no hay un partido para transmitir")
    return document


def live_score(match, projected):
    """Una proyección atrasada nunca hace retroceder el marcador oficial."""
    if projected and int(projected.get("ultimaSecuencia", -1)) == int(match["ultimaSecuencia"]):
        return {"local": int(projected["local"]), "visitante": int(projected["visitante"])}
    return dict(match["marcador"])


def telemetry_queries(match_id, player_id=None, team_id=None):
    """IDs provistos por el catálogo, validados antes de interpolar SQL."""
    for value, pattern in ((match_id, r"PAR-[0-9]{4}"), (player_id, r"JUG-[0-9]{4}"), (team_id, r"EQ-[0-9]{2}")):
        if value is not None and not re.fullmatch(pattern, value):
            raise DomainError(400, "INVALID_TELEMETRY_FILTER", "Filtro inválido")
    filters = f"partido_id = '{match_id}'"
    selected = filters
    if player_id:
        selected += f" AND jugador_id = '{player_id}'"
    if team_id:
        selected += f" AND equipo_id = '{team_id}'"
    return (
        "SELECT jugador_id, equipo_id, x, y, segundo_partido FROM posiciones_jugador WHERE "
        + filters + " AND segundo_partido = (SELECT MAX(segundo_partido) FROM posiciones_jugador WHERE "
        + filters + ") ORDER BY jugador_id LIMIT 22",
        "SELECT x, y, segundo_partido FROM posiciones_pelota WHERE " + filters + " ORDER BY time DESC LIMIT 1",
        "SELECT LEAST(19, CAST(FLOOR(x / 5) AS BIGINT)) AS cx, "
        "LEAST(11, CAST(FLOOR(y / (100.0 / 12)) AS BIGINT)) AS cy, COUNT(*) AS muestras "
        "FROM posiciones_jugador WHERE " + selected + " GROUP BY cx, cy LIMIT 240",
    )



def transmission(repo, redis_client, simulation_id=None, redis_errors=(OSError,)):
    doc = simulation_document(repo.db, simulation_id)
    match = repo.db.partidos.find_one({"_id": doc["partidoId"]})
    if match is None:
        raise DomainError(404, "MATCH_NOT_FOUND", "Partido inexistente")
    team_ids = [match["equipos"]["localId"], match["equipos"]["visitanteId"]]
    teams = {row["equipoId"]: row for row in repo.db.equipos.find(
        {"equipoId": {"$in": team_ids}}, {"_id": 0, "equipoId": 1, "nombre": 1, "codigoExterno": 1})}
    players = list(repo.db.jugadores.find(
        {"equipoId": {"$in": team_ids}},
        {"_id": 0, "jugadorId": 1, "equipoId": 1, "nombre": 1, "posicion": 1}))
    projected = {}
    try:
        projected = redis_client.hgetall(f"marcador:partido:{doc['partidoId']}")
    except redis_errors:
        pass
    return {
        "simulacion": repo._simulation_response(doc),
        "equipos": [teams.get(team, {"equipoId": team, "nombre": team}) for team in team_ids],
        "jugadores": players,
        "marcador": live_score(match, projected),
        "eventos": repo.list_events(doc["partidoId"], 0, 100)["items"],
        "actualizadoEn": datetime.now(timezone.utc),
    }


def transmission_comments(db, simulation_id, service):
    doc = simulation_document(db, simulation_id)
    anchor = doc["actualizadoEn"] if doc["estado"] == "FINALIZADA" else datetime.now(timezone.utc)
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=timezone.utc)
    items = {}
    for delta in range(3):
        bucket = (anchor - timedelta(minutes=delta)).strftime("%Y%m%d%H%M")
        page = service.list_by_match(doc["partidoId"], bucket, None, 100)
        for item in page["items"]:
            items[item["comentarioId"]] = item
    return {"items": sorted(items.values(), key=lambda row: row["creadoEn"], reverse=True)[:80]}
