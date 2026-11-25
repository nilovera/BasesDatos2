from pathlib import Path

from neo4j import GraphDatabase

from .config import settings


class Neo4jClient:
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database

    def health(self):
        self.driver.verify_connectivity()
        with self.driver.session(database=self.database) as session:
            value = session.run("RETURN 1 AS ok").single(strict=True)["ok"]
        return "UP" if value == 1 else "DOWN"

    def query_all(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            return [record.data() for record in session.run(query, parameters or {})]

    def query_one(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            record = session.run(query, parameters or {}).single()
            return None if record is None else record.data()


_driver = None
_client = None


def get_neo4j_client():
    global _driver, _client
    if _client is None:
        password = Path(settings.neo4j_password_file).read_text(encoding="utf-8").strip()
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, password),
            connection_timeout=settings.neo4j_timeout_seconds,
            max_connection_pool_size=20,
        )
        _client = Neo4jClient(_driver, settings.neo4j_database)
    return _client


def close_neo4j_client():
    global _driver, _client
    if _driver is not None:
        _driver.close()
    _driver = None
    _client = None
