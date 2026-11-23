import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .errors import DomainError


@dataclass(frozen=True)
class CacheRead:
    value: dict
    result: str


class RedisService:
    def __init__(self, client, redis_errors, cache_ttl_seconds=60):
        self.client = client
        self.redis_errors = redis_errors
        self.cache_ttl_seconds = cache_ttl_seconds

    @staticmethod
    def match_key(partido_id):
        return f"cache:partido:{partido_id}"

    @staticmethod
    def session_key(session_id):
        return f"sesion:{session_id}"

    def health(self):
        try:
            return "UP" if self.client.ping() else "DOWN"
        except self.redis_errors:
            return "DOWN"

    def get_match(self, partido_id, loader):
        key = self.match_key(partido_id)
        try:
            cached = self.client.get(key)
        except self.redis_errors:
            return CacheRead(loader(), "BYPASS")

        if cached is not None:
            self._record_match_read(partido_id)
            return CacheRead(json.loads(cached), "HIT")

        value = loader()
        try:
            self.client.set(key, json.dumps(value, separators=(",", ":")), ex=self.cache_ttl_seconds)
            self._record_match_read(partido_id)
        except self.redis_errors:
            return CacheRead(value, "BYPASS")
        return CacheRead(value, "MISS")

    def _record_match_read(self, partido_id):
        try:
            with self.client.pipeline(transaction=True) as pipeline:
                visits_key = f"contador:partido:{partido_id}:consultas"
                ranking_key = "ranking:partidos:consultas"
                pipeline.incr(visits_key)
                pipeline.expire(visits_key, 86400, nx=True)
                pipeline.zincrby(ranking_key, 1, partido_id)
                pipeline.expire(ranking_key, 86400, nx=True)
                pipeline.execute()
        except self.redis_errors:
            # Las metricas funcionales son derivadas y no deben impedir la lectura.
            pass

    def invalidate_match(self, partido_id):
        try:
            return bool(self.client.delete(self.match_key(partido_id)))
        except self.redis_errors:
            return False

    def create_session(self, usuario_id, rol, ttl_seconds):
        session_id = f"SES-{uuid4()}"
        key = self.session_key(session_id)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            with self.client.pipeline(transaction=True) as pipeline:
                pipeline.hset(
                    key,
                    mapping={
                        "sesionId": session_id,
                        "usuarioId": usuario_id,
                        "rol": rol,
                        "creadaEn": now,
                        "ultimoAcceso": now,
                        "renovaciones": "0",
                    },
                )
                pipeline.expire(key, ttl_seconds)
                pipeline.execute()
            return self.get_session(session_id)
        except self.redis_errors as error:
            raise DomainError(503, "REDIS_UNAVAILABLE", "Redis no respondió") from error

    def get_session(self, session_id):
        key = self.session_key(session_id)
        try:
            with self.client.pipeline(transaction=False) as pipeline:
                pipeline.hgetall(key)
                pipeline.ttl(key)
                data, ttl = pipeline.execute()
        except self.redis_errors as error:
            raise DomainError(503, "REDIS_UNAVAILABLE", "Redis no respondió") from error
        if not data or ttl == -2:
            raise DomainError(404, "SESSION_NOT_FOUND", "La sesión no existe o expiró")
        if ttl == -1:
            raise DomainError(500, "SESSION_WITHOUT_TTL", "La sesión no posee TTL")
        return {
            "sesionId": data["sesionId"],
            "usuarioId": data["usuarioId"],
            "rol": data["rol"],
            "creadaEn": data["creadaEn"],
            "ultimoAcceso": data["ultimoAcceso"],
            "renovaciones": int(data["renovaciones"]),
            "ttlSegundos": int(ttl),
        }

    def renew_session(self, session_id, ttl_seconds):
        key = self.session_key(session_id)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            renewed = self.client.eval(
                """
                if redis.call('EXISTS', KEYS[1]) == 0 then
                    return 0
                end
                redis.call('HSET', KEYS[1], 'ultimoAcceso', ARGV[1])
                redis.call('HINCRBY', KEYS[1], 'renovaciones', 1)
                redis.call('EXPIRE', KEYS[1], ARGV[2])
                return 1
                """,
                1,
                key,
                now,
                ttl_seconds,
            )
            if not renewed:
                raise DomainError(404, "SESSION_NOT_FOUND", "La sesión no existe o expiró")
            return self.get_session(session_id)
        except DomainError:
            raise
        except self.redis_errors as error:
            raise DomainError(503, "REDIS_UNAVAILABLE", "Redis no respondió") from error

    def delete_session(self, session_id):
        try:
            if not self.client.delete(self.session_key(session_id)):
                raise DomainError(404, "SESSION_NOT_FOUND", "La sesión no existe o expiró")
        except DomainError:
            raise
        except self.redis_errors as error:
            raise DomainError(503, "REDIS_UNAVAILABLE", "Redis no respondió") from error
