from __future__ import annotations

import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import iris.dbapi as iris_dbapi
import redis
from cassandra.cluster import Cluster
from neo4j import GraphDatabase
from pymongo import MongoClient

from app.config.settings import get_settings


settings = get_settings()


def check_mongodb() -> str:
    timeout_ms = int(settings.dependency_timeout_seconds * 1000)

    client = MongoClient(
        host=settings.mongodb_host,
        port=settings.mongodb_port,
        username=settings.mongodb_username,
        password=settings.mongodb_password.get_secret_value(),
        authSource=settings.mongodb_auth_source,
        serverSelectionTimeoutMS=timeout_ms,
        connectTimeoutMS=timeout_ms,
    )

    try:
        total = client[
            settings.mongodb_database
        ]["equipos"].count_documents({})

        return f"{total} equipos"
    finally:
        client.close()


def check_neo4j() -> str:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(
            settings.neo4j_username,
            settings.neo4j_password.get_secret_value(),
        ),
        connection_timeout=settings.dependency_timeout_seconds,
    )

    try:
        driver.verify_connectivity()

        with driver.session(
            database=settings.neo4j_database
        ) as session:
            record = session.run(
                "MATCH (equipo:Equipo) "
                "RETURN count(equipo) AS total"
            ).single()

            return f"{record['total']} equipos"
    finally:
        driver.close()


def check_cassandra() -> str:
    cluster = Cluster(
        contact_points=settings.cassandra_contact_points,
        port=settings.cassandra_port,
        connect_timeout=settings.dependency_timeout_seconds,
        control_connection_timeout=settings.dependency_timeout_seconds,
    )

    try:
        session = cluster.connect(settings.cassandra_keyspace)

        rows = session.execute(
            """
            SELECT table_name
            FROM system_schema.tables
            WHERE keyspace_name = %s
            """,
            [settings.cassandra_keyspace],
            timeout=settings.dependency_timeout_seconds,
        )

        return f"{len(list(rows))} tablas"
    finally:
        cluster.shutdown()


def check_redis() -> str:
    client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_database,
        socket_connect_timeout=settings.dependency_timeout_seconds,
        socket_timeout=settings.dependency_timeout_seconds,
        decode_responses=True,
    )

    try:
        pong = client.ping()
        total = client.dbsize()

        return f"PING={pong}; claves={total}"
    finally:
        client.close()


def check_influxdb() -> str:
    url = (
        settings.influxdb_url.rstrip("/")
        + "/api/v3/query_sql"
    )

    headers = {
        "Authorization": (
            "Bearer "
            + settings.influxdb_token.get_secret_value()
        )
    }

    payload = {
        "db": settings.influxdb_detail_database,
        "q": (
            "SELECT COUNT(*) AS total "
            "FROM estadisticas_equipo"
        ),
        "format": "json",
    }

    with httpx.Client(
        timeout=settings.dependency_timeout_seconds
    ) as client:
        response = client.post(
            url,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()
        rows = response.json()

    total = rows[0]["total"] if rows else 0
    return f"{total} puntos detallados"


def check_iris() -> str:
    connection = iris_dbapi.connect(
        settings.iris_host,
        settings.iris_port,
        settings.iris_namespace,
        settings.iris_username,
        settings.iris_password.get_secret_value(),
    )

    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM Fixture.Partido"
        )

        total = cursor.fetchone()[0]
        return f"{total} partidos"
    finally:
        cursor.close()
        connection.close()


def main() -> int:
    checks = [
        ("MongoDB", check_mongodb),
        ("Neo4j", check_neo4j),
        ("Cassandra", check_cassandra),
        ("Redis", check_redis),
        ("InfluxDB", check_influxdb),
        ("IRIS", check_iris),
    ]

    execution_time = datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    )

    print("=== HITO 10 - CONECTIVIDAD POLIGLOTA ===")
    print(
        "Fecha de ejecucion:",
        execution_time.isoformat(timespec="seconds"),
    )
    print()

    failures = 0

    for name, check in checks:
        started = time.perf_counter()

        try:
            result = check()
            duration_ms = (
                time.perf_counter() - started
            ) * 1000

            print(
                f"[OK] {name}: {result} "
                f"| duracion_ms={duration_ms:.2f}"
            )
        except Exception as error:
            failures += 1
            duration_ms = (
                time.perf_counter() - started
            ) * 1000

            print(
                f"[ERROR] {name}: "
                f"{type(error).__name__}: {error} "
                f"| duracion_ms={duration_ms:.2f}"
            )

    print()

    if failures:
        print(
            "=== RESULTADO: "
            f"{failures} DEPENDENCIA(S) CON ERROR ==="
        )
        return 1

    print("=== RESULTADO: 6 DE 6 DEPENDENCIAS DISPONIBLES ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())