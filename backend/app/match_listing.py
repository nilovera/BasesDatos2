"""Cartelera de partidos preparados y jugados, sin publicar el plan futuro."""

from .errors import DomainError

GROUPS = {
    "proximos": ["LISTA"],
    "en-curso": ["EJECUTANDO", "PAUSADA", "ERROR"],
    "finalizados": ["FINALIZADA"],
}


def team_catalog(db):
    return list(db.equipos.find({}, {
        "_id": 0, "equipoId": 1, "nombre": 1, "codigoExterno": 1,
    }).sort("nombre", 1))


def match_listing(db, group="proximos", page=0, limit=12):
    if group not in GROUPS or not 0 <= page <= 1000 or not 1 <= limit <= 50:
        raise DomainError(400, "INVALID_MATCH_PAGE", "Lista de partidos inválida")
    filters = {"estado": {"$in": GROUPS[group]}}
    projection = {"_id": 0, "simulacionId": 1, "partidoId": 1, "estado": 1,
                  "segundoPartido": 1, "creadoEn": 1}
    direction = 1 if group == "proximos" else -1
    rows = list(db.simulaciones.find(filters, projection).sort(
        [("creadoEn", direction), ("simulacionId", direction)]
    ).skip(page * limit).limit(limit + 1))
    has_more = len(rows) > limit
    rows = rows[:limit]
    matches = {row["partidoId"]: row for row in db.partidos.find(
        {"partidoId": {"$in": [row["partidoId"] for row in rows]}},
        {"_id": 0, "partidoId": 1, "equipos": 1, "marcador": 1},
    )}
    teams = {row["equipoId"]: row for row in team_catalog(db)}
    items = []
    for row in rows:
        match = matches.get(row["partidoId"])
        if match is None:
            continue
        items.append({
            "simulacionId": row["simulacionId"], "partidoId": row["partidoId"],
            "estado": row["estado"], "segundoPartido": int(row["segundoPartido"]),
            "creadoEn": row["creadoEn"], "marcador": match["marcador"],
            "equipos": [teams.get(match["equipos"][key], {
                "equipoId": match["equipos"][key], "nombre": match["equipos"][key],
            }) for key in ("localId", "visitanteId")],
        })
    return {"items": items, "pagina": page, "hayMas": has_more,
            "enCurso": db.simulaciones.count_documents({"estado": "EJECUTANDO"})}
