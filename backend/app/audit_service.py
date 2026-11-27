"""Historial en Cassandra por actor/dia y recurso/dia, sin consultas globales."""
import base64
import binascii
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from .errors import DomainError


def _date(value):
    when = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.astimezone(timezone.utc)


def _json(event):
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _fingerprint(event):
    # La fecha y el request ID de un reintento no reemplazan los originales.
    return {k: event[k] for k in ("actorId", "actorTipo", "accion", "recursoTipo",
                                 "recursoId", "resultado", "detalle")}


@dataclass(frozen=True)
class ReservedAudit:
    event: dict
    projected: bool


class CassandraAuditService:
    def __init__(self, session):
        self.session = session

    def reserve(self, event):
        row = self.session.execute(
            "INSERT INTO audit_operations (operation_id, event_json, projected) "
            "VALUES (%s, %s, false) IF NOT EXISTS",
            (event["operacionId"], _json(event)),
        ).one()
        values = row._asdict() if hasattr(row, "_asdict") else {}
        applied = values.get("[applied]", getattr(row, "applied", False))
        if applied:
            return ReservedAudit(event, False)
        stored = json.loads(row.event_json)
        if _fingerprint(stored) != _fingerprint(event):
            raise DomainError(409, "AUDIT_IDEMPOTENCY_CONFLICT", "La operacion de auditoria ya tiene otro contenido")
        return ReservedAudit(stored, bool(row.projected))

    def add_to_batch(self, batch, reserved):
        """Se comparte el batch acotado con publicar/moderar un comentario."""
        event = reserved.event
        when = _date(event["fecha"])
        day = when.strftime("%Y%m%d")
        event_id = UUID(event["auditoriaId"])
        payload = _json(event)
        batch.add(self.session.prepare(
            "INSERT INTO audit_by_actor_day (actor_id, day_bucket, occurred_at, audit_id, event_json) "
            "VALUES (?, ?, ?, ?, ?)"), (event["actorId"], day, when, event_id, payload))
        batch.add(self.session.prepare(
            "INSERT INTO audit_by_resource_day (resource_type, resource_id, day_bucket, occurred_at, audit_id, event_json) "
            "VALUES (?, ?, ?, ?, ?, ?)"),
            (event["recursoTipo"], event["recursoId"], day, when, event_id, payload))
        batch.add(self.session.prepare(
            "UPDATE audit_operations SET projected = true WHERE operation_id = ?"), (event["operacionId"],))

    def store(self, event):
        from cassandra import ConsistencyLevel
        from cassandra.query import BatchStatement, BatchType
        reserved = self.reserve(event)
        # Reproyectar es idempotente y tambien repara una vista incompleta.
        batch = BatchStatement(batch_type=BatchType.LOGGED,
                               consistency_level=ConsistencyLevel.LOCAL_ONE)
        self.add_to_batch(batch, reserved)
        self.session.execute(batch)

    @staticmethod
    def validate_day(day):
        try:
            if not re.fullmatch(r"[0-9]{8}", day):
                raise ValueError()
            datetime.strptime(day, "%Y%m%d")
        except (ValueError, TypeError):
            raise DomainError(400, "INVALID_AUDIT_DAY", "dia debe ser una fecha valida YYYYMMDD")

    @staticmethod
    def _cursor(event, scope):
        data = {"v": 1, "scope": scope, "t": event["fecha"], "id": event["auditoriaId"]}
        return base64.urlsafe_b64encode(_json(data).encode()).decode().rstrip("=")

    @staticmethod
    def _decode(cursor, scope):
        if not cursor:
            return None
        try:
            if len(cursor) > 2048:
                raise ValueError()
            data = json.loads(base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True))
            if not isinstance(data, dict) or data["v"] != 1 or data["scope"] != scope:
                raise ValueError()
            if not isinstance(data["t"], str) or not isinstance(data["id"], str):
                raise ValueError()
            when = _date(data["t"])
            if when.strftime("%Y%m%d") != scope[-1]:
                raise ValueError()
            return when, UUID(data["id"])
        except (ValueError, TypeError, KeyError, UnicodeError, binascii.Error):
            raise DomainError(400, "INVALID_AUDIT_CURSOR", "Cursor de auditoria invalido para esta consulta")

    def by_actor(self, actor, day, cursor=None, limit=50):
        return self._page("audit_by_actor_day", "actor_id = %s AND day_bucket = %s",
                          (actor, day), ["actor", actor, day], day, cursor, limit)

    def by_resource(self, kind, resource, day, cursor=None, limit=50):
        return self._page("audit_by_resource_day", "resource_type = %s AND resource_id = %s AND day_bucket = %s",
                          (kind, resource, day), ["resource", kind, resource, day], day, cursor, limit)

    def _page(self, table, where, params, scope, day, cursor, limit):
        self.validate_day(day)
        if not 1 <= limit <= 100:
            raise DomainError(400, "INVALID_AUDIT_LIMIT", "limite debe estar entre 1 y 100")
        after = self._decode(cursor, scope)
        base = f"SELECT event_json FROM {table} WHERE {where}"
        try:
            if after:
                when, event_id = after
                rows = list(self.session.execute(
                    base + " AND occurred_at = %s AND audit_id > %s LIMIT %s", params + (when, event_id, limit + 1)))
                rows += list(self.session.execute(
                    base + " AND occurred_at < %s LIMIT %s", params + (when, limit + 1)))
            else:
                rows = list(self.session.execute(base + " LIMIT %s", params + (limit + 1,)))
            events = [json.loads(row.event_json) for row in rows]
        except Exception as error:
            raise DomainError(503, "AUDIT_UNAVAILABLE", "No se pudo consultar la auditoria en Cassandra") from error
        events.sort(key=lambda x: (-_date(x["fecha"]).timestamp(), UUID(x["auditoriaId"]).int))
        page = events[:limit]
        return {"items": page, "siguienteCursor": self._cursor(page[-1], scope)
                if len(events) > limit else None}
