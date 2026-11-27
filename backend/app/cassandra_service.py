import base64
import binascii
import hashlib
import json
import zlib
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from .errors import DomainError
from .audit_context import make_audit_event
from .audit_service import CassandraAuditService, _date


MATCH_INSERT = """
INSERT INTO comments_by_match_bucket_shard
(match_id, bucket, shard, created_at, comment_id, user_id, content, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""
USER_INSERT = """
INSERT INTO comments_by_user_day
(user_id, day_bucket, created_at, comment_id, match_id, match_bucket,
 match_shard, content, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
LOCATOR_INSERT = """
INSERT INTO comment_locator_by_id
(comment_id, match_id, match_bucket, match_shard, user_id, day_bucket, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""


def utc_now():
    return datetime.now(timezone.utc)


def ensure_utc(value):
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def minute_bucket(value):
    return ensure_utc(value).strftime("%Y%m%d%H%M")


def day_bucket(value):
    return ensure_utc(value).strftime("%Y%m%d")


def stable_shard(user_id, shard_count=4):
    return zlib.crc32(user_id.encode("utf-8")) % shard_count


def encode_cursor(created_at, comment_id):
    payload = json.dumps(
        {
            "v": 1,
            "t": ensure_utc(created_at).isoformat().replace("+00:00", "Z"),
            "id": str(comment_id),
        },
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def decode_cursor(value):
    if value is None:
        return None
    try:
        padded = value + "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        if payload.get("v") != 1:
            raise ValueError("version de cursor no soportada")
        created_at = datetime.fromisoformat(payload["t"].replace("Z", "+00:00"))
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("cursor sin zona horaria")
        return ensure_utc(created_at), UUID(payload["id"])
    except (UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError, binascii.Error) as error:
        raise DomainError(
            400,
            "INVALID_COMMENT_CURSOR",
            "El cursor de comentarios no es válido",
        ) from error


def conditional_applied(row):
    values = row._asdict() if hasattr(row, "_asdict") else {}
    return bool(values.get("[applied]", getattr(row, "applied", False)))


class CassandraCommentService:
    def __init__(self, session, shard_count=4):
        self.session = session
        self.shard_count = shard_count

    def health(self):
        try:
            self.session.execute("SELECT release_version FROM system.local")
            return "UP"
        except Exception:
            return "DOWN"

    def publish(self, match_id, user_id, content, idempotency_key):
        from cassandra import ConsistencyLevel
        from cassandra.query import BatchStatement, BatchType

        created_at = utc_now()
        comment_id = uuid5(NAMESPACE_URL, f"fixture2030-comment:{idempotency_key}")
        payload = json.dumps(
            {"matchId": match_id, "userId": user_id, "content": content},
            sort_keys=True,
            separators=(",", ":"),
        )
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        try:
            result = self.session.execute(
                """
                INSERT INTO comment_write_requests
                (idempotency_key, payload_hash, comment_id, created_at)
                VALUES (%s, %s, %s, %s) IF NOT EXISTS
                """,
                (idempotency_key, payload_hash, comment_id, created_at),
            )
            row = result.one()
            replayed = not conditional_applied(row)
            if replayed:
                existing_hash = getattr(row, "payload_hash", None)
                if existing_hash != payload_hash:
                    raise DomainError(
                        409,
                        "IDEMPOTENCY_CONFLICT",
                        "La clave de idempotencia ya fue utilizada con otro contenido",
                    )
                created_at = ensure_utc(row.created_at)
                comment_id = row.comment_id

            match_bucket = minute_bucket(created_at)
            user_bucket = day_bucket(created_at)
            shard = stable_shard(user_id, self.shard_count)
            if replayed:
                locator = self.session.execute(
                    "SELECT * FROM comment_locator_by_id WHERE comment_id = %s",
                    (comment_id,),
                ).one()
                if locator is not None:
                    stored = self.session.execute(
                        """
                        SELECT content, status FROM comments_by_match_bucket_shard
                        WHERE match_id = %s AND bucket = %s AND shard = %s
                          AND created_at = %s AND comment_id = %s
                        """,
                        (match_id, match_bucket, shard, created_at, comment_id),
                    ).one()
                    if stored is not None:
                        return {
                            "comentarioId": str(comment_id),
                            "partidoId": match_id,
                            "usuarioId": user_id,
                            "contenido": stored.content if stored.status == "VISIBLE" else None,
                            "estado": stored.status,
                            "creadoEn": created_at,
                            "bucket": match_bucket,
                            "shard": shard,
                            "repetido": True,
                        }
            audit = CassandraAuditService(self.session)
            reserved = audit.reserve(make_audit_event(
                "PUBLICAR_COMENTARIO", "COMENTARIO", str(comment_id),
                operation_id="publicar:" + str(comment_id), occurred_at=created_at,
                declared_actor=user_id,
                detail={"partidoId": match_id, "autorComentario": user_id}))
            batch = BatchStatement(
                batch_type=BatchType.LOGGED,
                consistency_level=ConsistencyLevel.LOCAL_ONE,
            )
            batch.add(
                self.session.prepare(MATCH_INSERT),
                (match_id, match_bucket, shard, created_at, comment_id, user_id, content, "VISIBLE"),
            )
            batch.add(
                self.session.prepare(USER_INSERT),
                (
                    user_id,
                    user_bucket,
                    created_at,
                    comment_id,
                    match_id,
                    match_bucket,
                    shard,
                    content,
                    "VISIBLE",
                ),
            )
            batch.add(
                self.session.prepare(LOCATOR_INSERT),
                (comment_id, match_id, match_bucket, shard, user_id, user_bucket, created_at),
            )
            audit.add_to_batch(batch, reserved)
            self.session.execute(batch)
            return {
                "comentarioId": str(comment_id),
                "partidoId": match_id,
                "usuarioId": user_id,
                "contenido": content,
                "estado": "VISIBLE",
                "creadoEn": created_at,
                "bucket": match_bucket,
                "shard": shard,
                "repetido": replayed,
            }
        except DomainError:
            raise
        except Exception as error:
            raise DomainError(503, "CASSANDRA_UNAVAILABLE", "Cassandra no está disponible") from error

    @staticmethod
    def _take_eligible(results, limit, include_hidden):
        selected = []
        for result in results:
            for row in result:
                if include_hidden or row.status == "VISIBLE":
                    selected.append(row)
                    if len(selected) >= limit + 1:
                        return selected
        return selected

    def _match_partition_rows(
        self, match_id, bucket, shard, cursor, limit, include_hidden
    ):
        projection = """
            SELECT comment_id, match_id, user_id, content, status, created_at
            FROM comments_by_match_bucket_shard
        """
        if cursor is None:
            results = [
                self.session.execute(
                    projection
                    + " WHERE match_id = %s AND bucket = %s AND shard = %s",
                    (match_id, bucket, shard),
                )
            ]
        else:
            created_at, comment_id = cursor
            results = [
                self.session.execute(
                    projection
                    + """
                      WHERE match_id = %s AND bucket = %s AND shard = %s
                        AND created_at = %s AND comment_id > %s
                    """,
                    (match_id, bucket, shard, created_at, comment_id),
                ),
                self.session.execute(
                    projection
                    + """
                      WHERE match_id = %s AND bucket = %s AND shard = %s
                        AND created_at < %s
                    """,
                    (match_id, bucket, shard, created_at),
                ),
            ]
        return self._take_eligible(results, limit, include_hidden)

    def _user_partition_rows(self, user_id, bucket, cursor, limit, include_hidden):
        projection = """
            SELECT comment_id, match_id, user_id, content, status, created_at
            FROM comments_by_user_day
        """
        if cursor is None:
            results = [
                self.session.execute(
                    projection + " WHERE user_id = %s AND day_bucket = %s",
                    (user_id, bucket),
                )
            ]
        else:
            created_at, comment_id = cursor
            results = [
                self.session.execute(
                    projection
                    + """
                      WHERE user_id = %s AND day_bucket = %s
                        AND created_at = %s AND comment_id > %s
                    """,
                    (user_id, bucket, created_at, comment_id),
                ),
                self.session.execute(
                    projection
                    + """
                      WHERE user_id = %s AND day_bucket = %s
                        AND created_at < %s
                    """,
                    (user_id, bucket, created_at),
                ),
            ]
        return self._take_eligible(results, limit, include_hidden)

    def list_by_match(self, match_id, bucket, cursor_value, limit, include_hidden=False):
        cursor = decode_cursor(cursor_value)
        rows = []
        try:
            for shard in range(self.shard_count):
                rows.extend(
                    self._match_partition_rows(
                        match_id,
                        bucket,
                        shard,
                        cursor,
                        limit,
                        include_hidden,
                    )
                )
        except Exception as error:
            raise DomainError(503, "CASSANDRA_UNAVAILABLE", "Cassandra no está disponible") from error
        return self._page(rows, limit, include_hidden)

    def list_by_user(self, user_id, bucket, cursor_value, limit, include_hidden=False):
        cursor = decode_cursor(cursor_value)
        try:
            rows = self._user_partition_rows(
                user_id,
                bucket,
                cursor,
                limit,
                include_hidden,
            )
        except Exception as error:
            raise DomainError(503, "CASSANDRA_UNAVAILABLE", "Cassandra no está disponible") from error
        return self._page(rows, limit, include_hidden)

    def moderate(self, comment_id, status, moderator_id, reason, idempotency_key=None):
        from cassandra import ConsistencyLevel
        from cassandra.query import BatchStatement, BatchType

        try:
            locator = self.session.execute(
                "SELECT * FROM comment_locator_by_id WHERE comment_id = %s",
                (UUID(comment_id),),
            ).one()
            if locator is None:
                raise DomainError(404, "COMMENT_NOT_FOUND", "Comentario inexistente")
            audit = CassandraAuditService(self.session)
            # La clave opcional no se almacena en texto; cada accion nueva tiene otra identidad.
            operation_id = ("moderar:" + hashlib.sha256(idempotency_key.encode()).hexdigest()
                            if idempotency_key else "moderar:" + str(uuid4()))
            reserved = audit.reserve(make_audit_event(
                "MODERAR_COMENTARIO", "COMENTARIO", comment_id,
                operation_id=operation_id, declared_actor=moderator_id,
                detail={"partidoId": locator.match_id, "estado": status,
                        "motivoHash": hashlib.sha256(reason.encode()).hexdigest()}))
            moderated_at = _date(reserved.event["fecha"])
            if reserved.projected:
                # Un replay antiguo nunca revierte una moderacion posterior.
                return {"comentarioId": comment_id, "estado": status, "moderadoEn": moderated_at,
                        "moderadorId": moderator_id, "motivo": reason}
            batch = BatchStatement(
                batch_type=BatchType.LOGGED,
                consistency_level=ConsistencyLevel.LOCAL_ONE,
            )
            batch.add(
                self.session.prepare(
                    """
                    UPDATE comments_by_match_bucket_shard
                    SET status = ?, moderated_at = ?, moderator_id = ?, moderation_reason = ?
                    WHERE match_id = ? AND bucket = ? AND shard = ?
                      AND created_at = ? AND comment_id = ?
                    """
                ),
                (
                    status,
                    moderated_at,
                    moderator_id,
                    reason,
                    locator.match_id,
                    locator.match_bucket,
                    locator.match_shard,
                    locator.created_at,
                    locator.comment_id,
                ),
            )
            batch.add(
                self.session.prepare(
                    """
                    UPDATE comments_by_user_day
                    SET status = ?, moderated_at = ?, moderator_id = ?, moderation_reason = ?
                    WHERE user_id = ? AND day_bucket = ?
                      AND created_at = ? AND comment_id = ?
                    """
                ),
                (
                    status,
                    moderated_at,
                    moderator_id,
                    reason,
                    locator.user_id,
                    locator.day_bucket,
                    locator.created_at,
                    locator.comment_id,
                ),
            )
            audit.add_to_batch(batch, reserved)
            self.session.execute(batch)
            return {
                "comentarioId": comment_id,
                "estado": status,
                "moderadoEn": moderated_at,
                "moderadorId": moderator_id,
                "motivo": reason,
            }
        except DomainError:
            raise
        except Exception as error:
            raise DomainError(503, "CASSANDRA_UNAVAILABLE", "Cassandra no está disponible") from error

    @staticmethod
    def _page(rows, limit, include_hidden):
        visible = [row for row in rows if include_hidden or row.status == "VISIBLE"]
        visible.sort(
            key=lambda row: (
                -ensure_utc(row.created_at).timestamp(),
                UUID(str(row.comment_id)).int,
            )
        )
        has_more = len(visible) > limit
        selected = visible[:limit]
        items = [
            {
                "comentarioId": str(row.comment_id),
                "partidoId": row.match_id,
                "usuarioId": row.user_id,
                "contenido": row.content if row.status == "VISIBLE" else None,
                "estado": row.status,
                "creadoEn": ensure_utc(row.created_at),
            }
            for row in selected
        ]
        cursor = (
            encode_cursor(selected[-1].created_at, selected[-1].comment_id)
            if has_more and selected
            else None
        )
        return {"items": items, "siguienteCursor": cursor}
