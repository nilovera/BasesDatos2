import unittest

from backend.app.errors import DomainError
from backend.app.redis_service import RedisService


class FakePipeline:
    def __init__(self, client):
        self.client = client
        self.commands = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def _queue(self, name, *args, **kwargs):
        self.commands.append((name, args, kwargs))
        return self

    def hset(self, *args, **kwargs):
        return self._queue("hset", *args, **kwargs)

    def hgetall(self, *args, **kwargs):
        return self._queue("hgetall", *args, **kwargs)

    def ttl(self, *args, **kwargs):
        return self._queue("ttl", *args, **kwargs)

    def expire(self, *args, **kwargs):
        return self._queue("expire", *args, **kwargs)

    def incr(self, *args, **kwargs):
        return self._queue("incr", *args, **kwargs)

    def zincrby(self, *args, **kwargs):
        return self._queue("zincrby", *args, **kwargs)

    def execute(self):
        return [getattr(self.client, name)(*args, **kwargs) for name, args, kwargs in self.commands]


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.hashes = {}
        self.ttls = {}
        self.sorted_sets = {}

    def ping(self):
        return True

    def pipeline(self, transaction=True):
        return FakePipeline(self)

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, ex=None):
        self.values[key] = value
        if ex is not None:
            self.ttls[key] = ex
        return True

    def delete(self, key):
        existed = key in self.values or key in self.hashes
        self.values.pop(key, None)
        self.hashes.pop(key, None)
        self.ttls.pop(key, None)
        return int(existed)

    def hset(self, key, mapping):
        self.hashes.setdefault(key, {}).update({k: str(v) for k, v in mapping.items()})
        return len(mapping)

    def hgetall(self, key):
        return dict(self.hashes.get(key, {}))

    def ttl(self, key):
        if key not in self.hashes and key not in self.values:
            return -2
        return self.ttls.get(key, -1)

    def expire(self, key, seconds, nx=False):
        if key not in self.hashes and key not in self.values and key not in self.sorted_sets:
            return False
        if nx and key in self.ttls:
            return False
        self.ttls[key] = int(seconds)
        return True

    def incr(self, key):
        self.values[key] = str(int(self.values.get(key, "0")) + 1)
        return int(self.values[key])

    def zincrby(self, key, amount, member):
        values = self.sorted_sets.setdefault(key, {})
        values[member] = values.get(member, 0) + amount
        return values[member]

    def eval(self, _script, _keys, key, now, ttl):
        if key not in self.hashes:
            return 0
        self.hashes[key]["ultimoAcceso"] = now
        self.hashes[key]["renovaciones"] = str(
            int(self.hashes[key]["renovaciones"]) + 1
        )
        self.ttls[key] = int(ttl)
        return 1


class FailingRedis(FakeRedis):
    def get(self, _key):
        raise ConnectionError("down")


class RedisServiceTests(unittest.TestCase):
    def test_cache_aside_miss_then_hit(self):
        client = FakeRedis()
        service = RedisService(client, (ConnectionError,), 60)
        loads = []

        first = service.get_match("PAR-0001", lambda: loads.append(1) or {"version": 5})
        second = service.get_match("PAR-0001", lambda: loads.append(1) or {"version": 99})

        self.assertEqual("MISS", first.result)
        self.assertEqual("HIT", second.result)
        self.assertEqual({"version": 5}, second.value)
        self.assertEqual([1], loads)
        self.assertEqual(60, client.ttls["cache:partido:PAR-0001"])

    def test_cache_bypasses_redis_when_dependency_is_down(self):
        service = RedisService(FailingRedis(), (ConnectionError,), 60)
        result = service.get_match("PAR-0001", lambda: {"version": 5})
        self.assertEqual("BYPASS", result.result)
        self.assertEqual({"version": 5}, result.value)

    def test_invalidation_removes_cached_match(self):
        client = FakeRedis()
        service = RedisService(client, (ConnectionError,), 60)
        service.get_match("PAR-0001", lambda: {"version": 5})
        self.assertTrue(service.invalidate_match("PAR-0001"))
        self.assertNotIn("cache:partido:PAR-0001", client.values)

    def test_session_requires_explicit_renewal(self):
        client = FakeRedis()
        service = RedisService(client, (ConnectionError,), 60)
        created = service.create_session("USR-0001", "FAN", 120)
        session_id = created["sesionId"]

        read = service.get_session(session_id)
        self.assertEqual(120, read["ttlSegundos"])
        self.assertEqual(0, read["renovaciones"])

        renewed = service.renew_session(session_id, 600)
        self.assertEqual(600, renewed["ttlSegundos"])
        self.assertEqual(1, renewed["renovaciones"])

    def test_expired_session_is_not_recreated_by_renewal(self):
        service = RedisService(FakeRedis(), (ConnectionError,), 60)
        with self.assertRaises(DomainError) as context:
            service.renew_session("SES-inexistente", 600)
        self.assertEqual("SESSION_NOT_FOUND", context.exception.code)


if __name__ == "__main__":
    unittest.main()
