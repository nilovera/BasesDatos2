import time
from datetime import datetime, timezone
from uuid import UUID

import httpx
import pytest
import redis as redis_driver

from app.config.settings import get_settings


BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    with httpx.Client(
        base_url=BASE_URL,
        timeout=20.0,
        trust_env=False,
    ) as http_client:
        health = http_client.get("/health")

        if health.status_code != 200:
            pytest.fail(
                "La API debe estar ejecutándose antes "
                "de iniciar las pruebas."
            )

        yield http_client


@pytest.fixture()
def redis_client():
    settings = get_settings()

    connection = redis_driver.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_database,
        decode_responses=True,
        socket_connect_timeout=(
            settings.dependency_timeout_seconds
        ),
        socket_timeout=settings.dependency_timeout_seconds,
    )

    test_keys = [
        "sesion:SES-TEST-ACTIVA",
        "sesion:SES-TEST-CIERRE",
        "sesion:SES-TEST-EXPIRA",
    ]

    connection.delete(*test_keys)

    try:
        yield connection
    finally:
        connection.delete(*test_keys)
        connection.close()


def assert_observability(response: httpx.Response) -> None:
    request_id = response.headers.get("x-request-id")
    duration = response.headers.get("x-process-time-ms")

    assert request_id is not None
    UUID(request_id)

    assert duration is not None
    assert float(duration) >= 0


def create_session(
    redis_client,
    session_id: str,
    ttl_seconds: int,
) -> None:
    key = f"sesion:{session_id}"

    redis_client.hset(
        key,
        mapping={
            "sesion_id": session_id,
            "usuario_id": "USR-TEST",
            "rol": "fan",
            "ultimo_acceso": datetime.now(
                timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "estado": "activa",
            "partido_actual": "PAR-0001",
            "acciones": "1",
        },
    )

    redis_client.expire(key, ttl_seconds)


def test_01_health(client: httpx.Client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["estado"] == "ok"
    assert_observability(response)


def test_02_mongodb_equipo_existente(
    client: httpx.Client,
) -> None:
    response = client.get("/api/v1/equipos/EQ-01")

    assert response.status_code == 200

    body = response.json()

    assert body["codigo"] == "EQ-01"
    assert body["nombre"] == "Argentina"
    assert body["fuente_datos"] == "MongoDB"
    assert_observability(response)


def test_03_mongodb_equipo_inexistente(
    client: httpx.Client,
) -> None:
    response = client.get("/api/v1/equipos/EQ-99")

    assert response.status_code == 404
    assert "error" in response.json()
    assert_observability(response)


def test_04_mongodb_codigo_invalido(
    client: httpx.Client,
) -> None:
    response = client.get("/api/v1/equipos/ARG")

    assert response.status_code == 422
    assert response.json()["error"]["codigo"] == (
        "DATOS_INVALIDOS"
    )
    assert_observability(response)


def test_05_mongodb_paginacion(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/jugadores",
        params={
            "equipo_codigo": "EQ-01",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["datos"]) == 3
    assert body["paginacion"]["hay_mas"] is True
    assert body["paginacion"]["siguiente_cursor"]
    assert body["fuente_datos"] == "MongoDB"
    assert_observability(response)


def test_06_mongodb_pagina_vacia(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/jugadores",
        params={
            "equipo_codigo": "EQ-01",
            "cursor": "JUG-9999",
            "limit": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["datos"] == []
    assert_observability(response)


def test_07_neo4j_partido_existente(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-0001/eventos"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["codigo"] == "PAR-0001"
    assert len(body["equipos"]) == 2
    assert len(body["eventos"]) == 2
    assert body["fuente_datos"] == "Neo4j"
    assert_observability(response)


def test_08_neo4j_partido_inexistente(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-9999/eventos"
    )

    assert response.status_code == 404
    assert_observability(response)


def test_09_cassandra_paginacion(
    client: httpx.Client,
) -> None:
    first = client.get(
        "/api/v1/partidos/PAR-0001/comentarios",
        params={
            "bucket_10min": "203006131800",
            "limit": 1,
        },
    )

    assert first.status_code == 200

    first_body = first.json()
    page_state = first_body["paginacion"][
        "siguiente_page_state"
    ]

    assert len(first_body["datos"]) == 1
    assert page_state
    assert first_body["paginacion"]["hay_mas"] is True

    second = client.get(
        "/api/v1/partidos/PAR-0001/comentarios",
        params={
            "bucket_10min": "203006131800",
            "limit": 1,
            "page_state": page_state,
        },
    )

    assert second.status_code == 200
    assert len(second.json()["datos"]) == 1

    first_id = first_body["datos"][0]["comentario_id"]
    second_id = second.json()["datos"][0][
        "comentario_id"
    ]

    assert first_id != second_id
    assert_observability(first)
    assert_observability(second)


def test_10_cassandra_particion_vacia(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-9999/comentarios",
        params={
            "bucket_10min": "203006131800",
            "limit": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["datos"] == []
    assert_observability(response)


def test_11_cassandra_bucket_invalido(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-0001/comentarios",
        params={
            "bucket_10min": "203006131805",
            "limit": 3,
        },
    )

    assert response.status_code == 422
    assert_observability(response)


def test_12_redis_sesion_vigente(
    client: httpx.Client,
    redis_client,
) -> None:
    create_session(
        redis_client,
        "SES-TEST-ACTIVA",
        60,
    )

    response = client.get(
        "/api/v1/sesiones/SES-TEST-ACTIVA"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["sesion_id"] == "SES-TEST-ACTIVA"
    assert body["ttl_segundos"] > 0
    assert body["fuente_datos"] == "Redis"
    assert_observability(response)


def test_13_redis_cierre_explicito(
    client: httpx.Client,
    redis_client,
) -> None:
    create_session(
        redis_client,
        "SES-TEST-CIERRE",
        60,
    )

    close_response = client.delete(
        "/api/v1/sesiones/SES-TEST-CIERRE"
    )

    assert close_response.status_code == 200
    assert close_response.json()["cerrada"] is True

    get_response = client.get(
        "/api/v1/sesiones/SES-TEST-CIERRE"
    )

    assert get_response.status_code == 404
    assert_observability(close_response)
    assert_observability(get_response)


def test_14_redis_sesion_expirada(
    client: httpx.Client,
    redis_client,
) -> None:
    create_session(
        redis_client,
        "SES-TEST-EXPIRA",
        1,
    )

    time.sleep(2)

    response = client.get(
        "/api/v1/sesiones/SES-TEST-EXPIRA"
    )

    assert response.status_code == 404
    assert response.json()["error"]["codigo"] == (
        "SESION_NO_ENCONTRADA_O_EXPIRADA"
    )
    assert_observability(response)


def test_15_influxdb_detalle(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-0001/estadisticas",
        params={
            "desde": "2030-06-13T20:00:00Z",
            "hasta": "2030-06-13T20:01:00Z",
            "granularidad": "detalle",
            "equipo_id": "ARG",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["datos"]) == 6
    assert body["metadata"]["intervalo_fuente"] == (
        "10 segundos"
    )
    assert body["datos"][0]["time"].endswith("Z")
    assert body["fuente_datos"] == "InfluxDB"
    assert_observability(response)


def test_16_influxdb_resumen_15m(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-0001/estadisticas",
        params={
            "desde": "2030-06-13T20:00:00Z",
            "hasta": "2030-06-13T20:31:00Z",
            "granularidad": "15m",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["datos"]) == 6
    assert body["metadata"]["intervalo_fuente"] == (
        "15 minutos"
    )
    assert body["fuente_datos"] == "InfluxDB"
    assert_observability(response)


def test_17_influxdb_ventana_vacia(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-9999/estadisticas",
        params={
            "desde": "2030-06-13T20:00:00Z",
            "hasta": "2030-06-13T20:01:00Z",
            "granularidad": "detalle",
            "limit": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["datos"] == []
    assert_observability(response)


def test_18_influxdb_ventana_invalida(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-0001/estadisticas",
        params={
            "desde": "2030-06-13T21:00:00Z",
            "hasta": "2030-06-13T20:00:00Z",
            "granularidad": "detalle",
            "limit": 10,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["codigo"] == (
        "VENTANA_TEMPORAL_INVALIDA"
    )
    assert_observability(response)


def test_19_iris_partido_existente(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-0001/detalle"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["codigo"] == "PAR-0001"
    assert body["arbitro_principal"]["documento"] == (
        "ARB-0001"
    )
    assert len(body["eventos"]) == 1
    assert body["fuente_datos"] == (
        "InterSystems IRIS"
    )
    assert_observability(response)


def test_20_iris_partido_inexistente(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/partidos/PAR-9999/detalle"
    )

    assert response.status_code == 404
    assert_observability(response)


def test_21_limites_invalidos(
    client: httpx.Client,
) -> None:
    response = client.get(
        "/api/v1/jugadores",
        params={
            "equipo_codigo": "EQ-01",
            "limit": 101,
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["codigo"] == (
        "DATOS_INVALIDOS"
    )
    assert_observability(response)