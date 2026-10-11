import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POSTMAN_DIR = PROJECT_ROOT / "postman"
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "evidencia"

POSTMAN_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def test_script(
    expected_status: int,
    expected_source: str | None = None,
) -> list[str]:
    lines = [
        (
            f'pm.test("HTTP {expected_status}", '
            f'function () {{ pm.response.to.have.status('
            f'{expected_status}); }});'
        ),
        (
            'pm.test("Incluye X-Request-ID", function () { '
            'pm.expect(pm.response.headers.has('
            '"X-Request-ID")).to.eql(true); });'
        ),
        (
            'pm.test("Tiempo menor a 10 segundos", '
            'function () { '
            'pm.expect(pm.response.responseTime)'
            '.to.be.below(10000); });'
        ),
    ]

    if expected_source:
        lines.append(
            'pm.test("Fuente de datos correcta", '
            'function () { '
            'const body = pm.response.json(); '
            f'pm.expect(body.fuente_datos).to.eql('
            f'"{expected_source}"); }});'
        )

    return lines


def request_item(
    name: str,
    method: str,
    url: str,
    expected_status: int = 200,
    expected_source: str | None = None,
) -> dict:
    return {
        "name": name,
        "request": {
            "method": method,
            "header": [
                {
                    "key": "Accept",
                    "value": "application/json",
                }
            ],
            "url": "{{base_url}}" + url,
        },
        "event": [
            {
                "listen": "test",
                "script": {
                    "type": "text/javascript",
                    "exec": test_script(
                        expected_status,
                        expected_source,
                    ),
                },
            }
        ],
    }


items = [
    request_item(
        "Health",
        "GET",
        "/health",
    ),
    request_item(
        "MongoDB - Equipo",
        "GET",
        "/api/v1/equipos/EQ-01",
        expected_source="MongoDB",
    ),
    request_item(
        "MongoDB - Jugadores",
        "GET",
        (
            "/api/v1/jugadores"
            "?equipo_codigo=EQ-01&limit=3"
        ),
        expected_source="MongoDB",
    ),
    request_item(
        "Neo4j - Partido y eventos",
        "GET",
        "/api/v1/partidos/PAR-0001/eventos",
        expected_source="Neo4j",
    ),
    request_item(
        "Cassandra - Comentarios",
        "GET",
        (
            "/api/v1/partidos/PAR-0001/comentarios"
            "?bucket_10min=203006131800&limit=3"
        ),
        expected_source="Cassandra",
    ),
    request_item(
        "Redis - Consultar sesion",
        "GET",
        "/api/v1/sesiones/SES-POSTMAN-0001",
        expected_source="Redis",
    ),
    request_item(
        "InfluxDB - Estadisticas",
        "GET",
        (
            "/api/v1/partidos/PAR-0001/estadisticas"
            "?desde=2030-06-13T20%3A00%3A00Z"
            "&hasta=2030-06-13T20%3A01%3A00Z"
            "&granularidad=detalle"
            "&equipo_id=ARG"
            "&limit=10"
        ),
        expected_source="InfluxDB",
    ),
    request_item(
        "IRIS - Detalle persistente",
        "GET",
        "/api/v1/partidos/PAR-0001/detalle",
        expected_source="InterSystems IRIS",
    ),
    request_item(
        "Redis - Cerrar sesion",
        "DELETE",
        "/api/v1/sesiones/SES-POSTMAN-0001",
        expected_source="Redis",
    ),
]

collection = {
    "info": {
        "_postman_id": (
            "6c5ed12e-70a5-4c15-"
            "9f1f-2030a10f0001"
        ),
        "name": "Fixture 2030 - Hito 10",
        "description": (
            "Coleccion de pruebas de la API REST "
            "integrada con seis motores de datos."
        ),
        "schema": (
            "https://schema.getpostman.com/"
            "json/collection/v2.1.0/"
            "collection.json"
        ),
    },
    "variable": [
        {
            "key": "base_url",
            "value": "http://127.0.0.1:8000",
            "type": "string",
        }
    ],
    "item": items,
}

environment = {
    "id": "56d33d57-b6c0-4d3c-91dc-2030a10f0002",
    "name": "Fixture 2030 - Local",
    "values": [
        {
            "key": "base_url",
            "value": "http://127.0.0.1:8000",
            "type": "default",
            "enabled": True,
        }
    ],
    "_postman_variable_scope": "environment",
    "_postman_exported_at": datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    ).isoformat(timespec="seconds"),
    "_postman_exported_using": "Fixture 2030 Hito 10",
}

collection_path = (
    POSTMAN_DIR
    / "Fixture2030.postman_collection.json"
)
environment_path = (
    POSTMAN_DIR
    / "Fixture2030.postman_environment.json"
)

collection_path.write_text(
    json.dumps(
        collection,
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

environment_path.write_text(
    json.dumps(
        environment,
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

generated_at = datetime.now(
    ZoneInfo("America/Argentina/Buenos_Aires")
).isoformat(timespec="seconds")

evidence = "\n".join(
    [
        "=== HITO 10 - COLECCION POSTMAN ===",
        f"Fecha de ejecucion: {generated_at}",
        f"Solicitudes incluidas: {len(items)}",
        "Motores cubiertos: 6",
        "",
        "=== SOLICITUDES ===",
        *[
            (
                f"{item['request']['method']:6} "
                f"{item['name']}"
            )
            for item in items
        ],
        "",
        "=== ARCHIVOS GENERADOS ===",
        str(collection_path),
        str(environment_path),
    ]
) + "\n"

evidence_path = (
    EVIDENCE_DIR / "12_postman_coleccion.txt"
)

evidence_path.write_text(
    evidence,
    encoding="utf-8",
)

print(evidence)
print(f"Evidencia: {evidence_path}")
