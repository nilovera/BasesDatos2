from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from bson.int64 import Int64
from pymongo import ASCENDING, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from .config import settings
from .domain import apply_event, canonical_request_hash
from .errors import DomainError


@dataclass(frozen=True)
class EventWriteResult:
    body: dict
    replayed: bool
    status: int


def _iso(value):
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _match_response(document):
    return {
        "partidoId": document["partidoId"],
        "localId": document["equipos"]["localId"],
        "visitanteId": document["equipos"]["visitanteId"],
        "inicioProgramado": _iso(document["inicioProgramado"]),
        "estado": document["estado"],
        "marcador": document["marcador"],
        "version": int(document["version"]),
    }


class MongoRepository:
    def __init__(self, client):
        self.client = client
        self.db = client.get_database(settings.mongodb_database)

    def health_status(self):
        try:
            hello = self.client.admin.command("hello")
        except PyMongoError:
            return "DOWN"
        if hello.get("setName") != "rs0" or not hello.get("isWritablePrimary"):
            return "DOWN"
        return "PRIMARY"

    def health(self):
        status = self.health_status()
        if status == "DOWN":
            raise DomainError(
                503, "OFFICIAL_STORE_UNAVAILABLE", "MongoDB no respondió"
            )
        return {"status": "UP", "service": "fixture2030-api", "mongodb": status}

    def get_match(self, partido_id):
        try:
            document = self.db.partidos.find_one({"_id": partido_id})
        except PyMongoError as error:
            raise DomainError(
                503, "OFFICIAL_STORE_UNAVAILABLE", "MongoDB no respondió"
            ) from error
        if document is None:
            raise DomainError(404, "MATCH_NOT_FOUND", "El partido no existe")
        return _match_response(document)

    def validate_match_teams(self, partido_id, team_ids):
        try:
            match = self.db.partidos.find_one(
                {"_id": partido_id},
                {"equipos": 1},
            )
        except PyMongoError as error:
            raise DomainError(
                503, "OFFICIAL_STORE_UNAVAILABLE", "MongoDB no respondió"
            ) from error
        if match is None:
            raise DomainError(404, "MATCH_NOT_FOUND", "El partido no existe")
        participants = {
            match["equipos"]["localId"],
            match["equipos"]["visitanteId"],
        }
        invalid = sorted(set(team_ids) - participants)
        if invalid:
            raise DomainError(
                422,
                "TEAM_NOT_IN_MATCH",
                "Uno o más equipos no participan del partido",
                {"equipos": invalid},
            )
        return participants

    def validate_position_references(self, partido_id, samples):
        self.validate_match_teams(
            partido_id, [sample.equipo_id for sample in samples]
        )
        player_ids = sorted({sample.jugador_id for sample in samples})
        try:
            players = {
                item["jugadorId"]: item["equipoId"]
                for item in self.db.jugadores.find(
                    {"jugadorId": {"$in": player_ids}, "activo": True},
                    {"jugadorId": 1, "equipoId": 1},
                )
            }
        except PyMongoError as error:
            raise DomainError(
                503, "OFFICIAL_STORE_UNAVAILABLE", "MongoDB no respondió"
            ) from error
        missing = sorted(set(player_ids) - set(players))
        if missing:
            raise DomainError(
                422,
                "PLAYER_NOT_FOUND",
                "Uno o más jugadores no existen o están inactivos",
                {"jugadores": missing},
            )
        mismatches = sorted(
            sample.jugador_id
            for sample in samples
            if players[sample.jugador_id] != sample.equipo_id
        )
        if mismatches:
            raise DomainError(
                422,
                "PLAYER_TEAM_MISMATCH",
                "Uno o más jugadores no pertenecen al equipo informado",
                {"jugadores": sorted(set(mismatches))},
            )

    def list_events(self, partido_id, desde_secuencia, limite):
        try:
            if not self.db.partidos.find_one({"_id": partido_id}, {"_id": 1}):
                raise DomainError(404, "MATCH_NOT_FOUND", "El partido no existe")
            documents = list(
                self.db.eventos_oficiales.find(
                    {
                        "partidoId": partido_id,
                        "secuencia": {"$gt": desde_secuencia},
                    },
                    {"eventoId": 1, "secuencia": 1, "tipo": 1, "ocurridoEn": 1},
                )
                .sort([("secuencia", ASCENDING)])
                .limit(limite + 1)
            )
        except DomainError:
            raise
        except PyMongoError as error:
            raise DomainError(
                503, "OFFICIAL_STORE_UNAVAILABLE", "MongoDB no respondió"
            ) from error

        has_more = len(documents) > limite
        page = documents[:limite]
        return {
            "items": [
                {
                    "eventoId": item["eventoId"],
                    "secuencia": int(item["secuencia"]),
                    "tipo": item["tipo"],
                    "ocurridoEn": _iso(item["ocurridoEn"]),
                }
                for item in page
            ],
            "siguienteSecuencia": int(page[-1]["secuencia"])
            if has_more and page
            else None,
        }

    def _player_teams(self, payload, session):
        player_ids = set()
        for key in ("jugadorId", "saleJugadorId", "entraJugadorId"):
            if payload.get(key):
                player_ids.add(payload[key])
        replacement = payload.get("reemplazo") or {}
        for key in ("jugadorId", "saleJugadorId", "entraJugadorId"):
            if replacement.get(key):
                player_ids.add(replacement[key])
        if not player_ids:
            return {}
        return {
            item["jugadorId"]: item["equipoId"]
            for item in self.db.jugadores.find(
                {"jugadorId": {"$in": list(player_ids)}, "activo": True},
                {"jugadorId": 1, "equipoId": 1},
                session=session,
            )
        }

    def _replay_or_conflict(self, existing, request_hash):
        if existing["idempotencia"]["hashSolicitud"] != request_hash:
            raise DomainError(
                409,
                "IDEMPOTENCY_KEY_REUSED",
                "La clave idempotente ya fue utilizada con otro contenido",
            )
        return EventWriteResult(
            body=existing["respuestaHttp"]["body"], replayed=True, status=200
        )

    def register_event(self, partido_id, idempotency_key, payload, occurred_at):
        request_hash = canonical_request_hash(
            "POST",
            f"/api/v1/partidos/{partido_id}/eventos",
            partido_id,
            payload,
        )

        def transaction(session):
            existing = self.db.eventos_oficiales.find_one(
                {"idempotencia.clave": idempotency_key}, session=session
            )
            if existing:
                return self._replay_or_conflict(existing, request_hash)

            match = self.db.partidos.find_one({"_id": partido_id}, session=session)
            if match is None:
                raise DomainError(404, "MATCH_NOT_FOUND", "El partido no existe")

            original_document = None
            original_event = None
            if payload["tipo"] == "CORRECCION_EVENTO":
                original_document = self.db.eventos_oficiales.find_one(
                    {
                        "eventoId": payload["eventoOriginalId"],
                        "partidoId": partido_id,
                    },
                    session=session,
                )
                if original_document:
                    previous_correction = self.db.eventos_oficiales.find_one(
                        {
                            "partidoId": partido_id,
                            "referencia.eventoOriginalId": original_document["eventoId"],
                        },
                        {"eventoId": 1},
                        session=session,
                    )
                    if previous_correction:
                        raise DomainError(
                            409,
                            "EVENT_ALREADY_CORRECTED",
                            "El evento ya posee una corrección oficial",
                            {"correccionId": previous_correction["eventoId"]},
                        )
                    original_event = {
                        "tipo": original_document["tipo"],
                        **original_document["datos"],
                    }

            player_teams = self._player_teams(payload, session)
            updated = apply_event(match, payload, player_teams, original_event)
            now = datetime.now(timezone.utc)

            counter = self.db.contadores.find_one_and_update(
                {"_id": "eventos"},
                {"$inc": {"valor": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
                session=session,
            )
            event_number = int(counter["valor"])
            if event_number > 999999:
                raise DomainError(503, "EVENT_ID_EXHAUSTED", "Se agotó el rango de eventos")
            event_id = f"EVE-{event_number:06d}"
            sequence = int(updated["ultimaSecuencia"])
            version = int(updated["version"])

            match_fields = {
                "estado": updated["estado"],
                "marcador": updated["marcador"],
                "ultimaSecuencia": Int64(sequence),
                "version": Int64(version),
                "actualizadoEn": now,
            }
            if "inicioReal" in updated:
                match_fields["inicioReal"] = occurred_at

            update_result = self.db.partidos.update_one(
                {"_id": partido_id, "version": match["version"]},
                {"$set": match_fields},
                session=session,
            )
            if update_result.modified_count != 1:
                raise DomainError(
                    409,
                    "VERSION_CONFLICT",
                    "Otra operación modificó el partido",
                )

            response = {
                "eventoId": event_id,
                "partidoId": partido_id,
                "secuencia": sequence,
                "tipo": payload["tipo"],
                "estadoPartido": updated["estado"],
                "marcador": updated["marcador"],
                "versionPartido": version,
                "propagacion": "PENDIENTE",
            }
            data = {
                key: value
                for key, value in payload.items()
                if key not in {"tipo", "ocurridoEn", "eventoOriginalId"}
            }
            event_document = {
                "_id": event_id,
                "eventoId": event_id,
                "partidoId": partido_id,
                "secuencia": Int64(sequence),
                "tipo": payload["tipo"],
                "datos": data,
                "idempotencia": {
                    "clave": idempotency_key,
                    "hashSolicitud": request_hash,
                },
                "ocurridoEn": occurred_at,
                "recibidoEn": now,
                "versionContrato": 1,
                "respuestaHttp": {"status": 201, "body": response},
            }
            if original_document:
                event_document["referencia"] = {
                    "eventoOriginalId": original_document["eventoId"]
                }
            self.db.eventos_oficiales.insert_one(event_document, session=session)

            outbox_id = str(uuid4())
            self.db.outbox.insert_one(
                {
                    "_id": outbox_id,
                    "outboxId": outbox_id,
                    "eventoId": event_id,
                    "partidoId": partido_id,
                    "tipo": payload["tipo"],
                    "secuencia": Int64(sequence),
                    "payload": {"evento": payload, "resultado": response},
                    "versionContrato": 1,
                    "estado": "PENDIENTE",
                    "intentos": 0,
                    "proximoIntentoEn": now,
                    "ultimoError": None,
                    "creadoEn": now,
                    "actualizadoEn": now,
                    "publicadoEn": None,
                    "expiraEn": None,
                },
                session=session,
            )
            return EventWriteResult(body=response, replayed=False, status=201)

        try:
            with self.client.start_session() as session:
                return session.with_transaction(
                    transaction,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority", wtimeout=5000),
                    read_preference=ReadPreference.PRIMARY,
                )
        except DomainError:
            raise
        except DuplicateKeyError:
            existing = self.db.eventos_oficiales.find_one(
                {"idempotencia.clave": idempotency_key}
            )
            if existing:
                return self._replay_or_conflict(existing, request_hash)
            raise DomainError(409, "VERSION_CONFLICT", "Conflicto de escritura")
        except PyMongoError as error:
            raise DomainError(
                503,
                "OFFICIAL_STORE_UNAVAILABLE",
                "MongoDB no pudo confirmar la operación",
            ) from error

    def pending_outbox(self):
        return self.db.outbox.count_documents({"estado": "PENDIENTE"})

    def datamart_snapshot(self):
        """Extrae un corte consistente a nivel de documento para el ETL por lote."""
        try:
            teams = list(self.db.equipos.find(
                {"activo": True}, {"_id": 0, "equipoId": 1, "nombre": 1, "confederacion": 1}
            ).sort("equipoId", ASCENDING))
            players = list(self.db.jugadores.find(
                {"activo": True}, {"_id": 0, "jugadorId": 1, "equipoId": 1, "nombre": 1, "posicion": 1}
            ).sort("jugadorId", ASCENDING))
            matches = [
                {
                    "partidoId": item["partidoId"],
                    "localId": item["equipos"]["localId"],
                    "visitanteId": item["equipos"]["visitanteId"],
                    "inicioProgramado": item["inicioProgramado"],
                    "estado": item["estado"],
                }
                for item in self.db.partidos.find({}).sort("partidoId", ASCENDING)
            ]
            raw_events = list(self.db.eventos_oficiales.find({}).sort(
                [("partidoId", ASCENDING), ("secuencia", ASCENDING)]
            ))
        except PyMongoError as error:
            raise DomainError(503, "OFFICIAL_STORE_UNAVAILABLE", "MongoDB no respondió") from error

        corrected = {
            event.get("referencia", {}).get("eventoOriginalId")
            for event in raw_events if event["tipo"] == "CORRECCION_EVENTO"
        }
        events = []
        for event in raw_events:
            if event["eventoId"] in corrected:
                continue
            data = dict(event.get("datos") or {})
            event_type = event["tipo"]
            origin = None
            if event_type == "CORRECCION_EVENTO":
                origin = event.get("referencia", {}).get("eventoOriginalId")
                replacement = data.get("reemplazo") or {}
                event_type = replacement.get("tipo", event_type)
                data = replacement
            events.append({
                "eventoId": event["eventoId"], "partidoId": event["partidoId"],
                "secuencia": int(event["secuencia"]), "tipo": event_type,
                "ocurridoEn": event["ocurridoEn"], "equipoId": data.get("equipoId"),
                "jugadorId": data.get("jugadorId"), "eventoOrigenId": origin,
                "goles": 1 if event_type == "GOL" else 0,
                "asistencias": 1 if event_type == "GOL" and data.get("asistenteJugadorId") else 0,
            })
        return {"equipos": teams, "jugadores": players, "partidos": matches, "eventos": events}

    def operational_goals_by_team(self):
        snapshot = self.datamart_snapshot()
        names = {team["equipoId"]: team["nombre"] for team in snapshot["equipos"]}
        counts = {}
        for event in snapshot["eventos"]:
            if event["goles"] and event.get("equipoId"):
                counts[event["equipoId"]] = counts.get(event["equipoId"], 0) + 1
        return {
            "fuente": "OPERACIONAL",
            "items": [
                {"equipoId": team_id, "nombre": names.get(team_id, team_id), "goles": goals}
                for team_id, goals in sorted(counts.items(), key=lambda row: (-row[1], row[0]))
            ],
        }
