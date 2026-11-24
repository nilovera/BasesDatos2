from threading import Lock

from .config import settings


_cluster = None
_session = None
_lock = Lock()


def get_cassandra_session():
    global _cluster, _session
    if _session is None:
        with _lock:
            if _session is None:
                from cassandra.cluster import Cluster

                _cluster = Cluster(
                    [settings.cassandra_host],
                    port=settings.cassandra_port,
                    connect_timeout=settings.cassandra_timeout_seconds,
                )
                _session = _cluster.connect(settings.cassandra_keyspace)
                _session.default_timeout = settings.cassandra_timeout_seconds
    return _session


def close_cassandra_client():
    global _cluster, _session
    if _session is not None:
        _session.shutdown()
    if _cluster is not None:
        _cluster.shutdown()
    _session = None
    _cluster = None

