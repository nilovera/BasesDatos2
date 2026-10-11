import csv
import json
import math
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "evidencia"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

WARMUP_REQUESTS = 1
MEASURED_REQUESTS = 10
TIMEOUT_SECONDS = 10.0

ENDPOINTS = [
    {
        "motor": "MongoDB",
        "endpoint": "/api/v1/equipos/EQ-01",
    },
    {
        "motor": "Neo4j",
        "endpoint": (
            "/api/v1/partidos/"
            "PAR-0001/eventos"
        ),
    },
    {
        "motor": "Cassandra",
        "endpoint": (
            "/api/v1/partidos/"
            "PAR-0001/comentarios"
            "?bucket_10min=203006131800"
            "&limit=3"
        ),
    },
    {
        "motor": "Redis",
        "endpoint": (
            "/api/v1/sesiones/"
            "SES-PERF-0001"
        ),
    },
    {
        "motor": "InfluxDB",
        "endpoint": (
            "/api/v1/partidos/"
            "PAR-0001/estadisticas"
            "?desde=2030-06-13T20%3A00%3A00Z"
            "&hasta=2030-06-13T20%3A01%3A00Z"
            "&granularidad=detalle"
            "&equipo_id=ARG"
            "&limit=10"
        ),
    },
    {
        "motor": "InterSystems IRIS",
        "endpoint": (
            "/api/v1/partidos/"
            "PAR-0001/detalle"
        ),
    },
]


def percentile_nearest_rank(
    values: list[float],
    percentile: float,
) -> float:
    ordered = sorted(values)
    position = math.ceil(
        percentile * len(ordered)
    )
    index = max(0, position - 1)
    return ordered[index]


def main() -> int:
    generated_at = datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    ).isoformat(timespec="seconds")

    hardware = {
        "procesador": os.getenv(
            "HITO10_CPU_NAME",
            "No informado",
        ),
        "nucleos_fisicos": os.getenv(
            "HITO10_CPU_CORES",
            "No informado",
        ),
        "procesadores_logicos": os.getenv(
            "HITO10_CPU_LOGICAL",
            "No informado",
        ),
        "ram_gb": os.getenv(
            "HITO10_RAM_GB",
            "No informado",
        ),
    }

    raw_rows = []
    summaries = []
    failures = 0
    all_durations = []

    with httpx.Client(
        base_url=BASE_URL,
        timeout=TIMEOUT_SECONDS,
    ) as client:
        for definition in ENDPOINTS:
            motor = definition["motor"]
            endpoint = definition["endpoint"]

            for _ in range(WARMUP_REQUESTS):
                warmup_response = client.get(endpoint)

                if warmup_response.status_code != 200:
                    print(
                        f"[ERROR] Calentamiento "
                        f"{motor}: HTTP "
                        f"{warmup_response.status_code}"
                    )
                    return 1

            durations = []
            successful = 0

            for iteration in range(
                1,
                MEASURED_REQUESTS + 1,
            ):
                started = time.perf_counter()

                try:
                    response = client.get(endpoint)
                    duration_ms = (
                        time.perf_counter() - started
                    ) * 1000

                    status_code = response.status_code
                    success = status_code == 200
                except Exception as error:
                    duration_ms = (
                        time.perf_counter() - started
                    ) * 1000

                    status_code = 0
                    success = False

                    print(
                        f"[ERROR] {motor}: "
                        f"{type(error).__name__}: "
                        f"{error}"
                    )

                durations.append(duration_ms)
                all_durations.append(duration_ms)

                if success:
                    successful += 1
                else:
                    failures += 1

                raw_rows.append(
                    {
                        "fecha_ejecucion": generated_at,
                        "motor": motor,
                        "iteracion": iteration,
                        "metodo": "GET",
                        "endpoint": endpoint,
                        "status_code": status_code,
                        "duracion_ms": round(
                            duration_ms,
                            2,
                        ),
                        "exitosa": success,
                    }
                )

            average_ms = statistics.mean(durations)

            summaries.append(
                {
                    "motor": motor,
                    "solicitudes": len(durations),
                    "exitosas": successful,
                    "promedio_ms": round(
                        average_ms,
                        2,
                    ),
                    "mediana_ms": round(
                        statistics.median(durations),
                        2,
                    ),
                    "p95_ms": round(
                        percentile_nearest_rank(
                            durations,
                            0.95,
                        ),
                        2,
                    ),
                    "minimo_ms": round(
                        min(durations),
                        2,
                    ),
                    "maximo_ms": round(
                        max(durations),
                        2,
                    ),
                    "rps_secuencial_estimado": round(
                        1000 / average_ms,
                        2,
                    ),
                }
            )

    csv_path = (
        EVIDENCE_DIR / "14_rendimiento_api.csv"
    )
    json_path = (
        EVIDENCE_DIR / "14_rendimiento_api.json"
    )
    text_path = (
        EVIDENCE_DIR / "14_rendimiento_api.txt"
    )

    with csv_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(raw_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(raw_rows)

    report = {
        "fecha_ejecucion": generated_at,
        "entorno": "local",
        "base_url": BASE_URL,
        "hardware": hardware,
        "metodo": {
            "tipo": "medicion HTTP extremo a extremo",
            "concurrencia": 1,
            "solicitudes_calentamiento_por_motor": (
                WARMUP_REQUESTS
            ),
            "solicitudes_medidas_por_motor": (
                MEASURED_REQUESTS
            ),
            "timeout_segundos": TIMEOUT_SECONDS,
            "incluye": (
                "API, adaptador, red local y "
                "consulta al motor"
            ),
        },
        "resultados": summaries,
        "resultado_general": {
            "solicitudes_totales": len(raw_rows),
            "solicitudes_exitosas": (
                len(raw_rows) - failures
            ),
            "solicitudes_fallidas": failures,
            "promedio_general_ms": round(
                statistics.mean(all_durations),
                2,
            ),
        },
    }

    json_path.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "=== HITO 10 - MEDICION DE RENDIMIENTO ===",
        f"Fecha de ejecucion: {generated_at}",
        "",
        "=== HARDWARE ===",
        f"Procesador: {hardware['procesador']}",
        (
            "Nucleos fisicos: "
            f"{hardware['nucleos_fisicos']}"
        ),
        (
            "Procesadores logicos: "
            f"{hardware['procesadores_logicos']}"
        ),
        f"RAM GB: {hardware['ram_gb']}",
        "",
        "=== METODO ===",
        "Tipo: HTTP extremo a extremo",
        "Concurrencia: 1",
        (
            "Calentamiento por motor: "
            f"{WARMUP_REQUESTS}"
        ),
        (
            "Solicitudes medidas por motor: "
            f"{MEASURED_REQUESTS}"
        ),
        (
            "Total de solicitudes medidas: "
            f"{len(raw_rows)}"
        ),
        f"Timeout: {TIMEOUT_SECONDS} segundos",
        (
            "Incluye: API, adaptador, red local "
            "y consulta al motor"
        ),
        "",
        "=== RESULTADOS ===",
        (
            "Motor               Exito  Prom.   "
            "Mediana  P95     Min.    Max."
        ),
    ]

    for result in summaries:
        lines.append(
            f"{result['motor']:<19} "
            f"{result['exitosas']:>2}/"
            f"{result['solicitudes']:<2} "
            f"{result['promedio_ms']:>7.2f} "
            f"{result['mediana_ms']:>8.2f} "
            f"{result['p95_ms']:>7.2f} "
            f"{result['minimo_ms']:>7.2f} "
            f"{result['maximo_ms']:>7.2f}"
        )

    lines.extend(
        [
            "",
            "=== RESULTADO GENERAL ===",
            (
                "Solicitudes exitosas: "
                f"{len(raw_rows) - failures}/"
                f"{len(raw_rows)}"
            ),
            (
                "Promedio general ms: "
                f"{statistics.mean(all_durations):.2f}"
            ),
            (
                "Resultado: "
                + (
                    "APROBADO"
                    if failures == 0
                    else "CON FALLOS"
                )
            ),
            "",
            "=== EVIDENCIAS VINCULADAS ===",
            str(text_path),
            str(csv_path),
            str(json_path),
        ]
    )

    text_report = "\n".join(lines) + "\n"

    text_path.write_text(
        text_report,
        encoding="utf-8",
    )

    print(text_report)

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
