import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_DIR = PROJECT_ROOT / "openapi"
EVIDENCE_DIR = PROJECT_ROOT / "docs" / "evidencia"

OPENAPI_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

generated_at = datetime.now(
    ZoneInfo("America/Argentina/Buenos_Aires")
).isoformat(timespec="seconds")

schema = app.openapi()

schema["servers"] = [
    {
        "url": "http://127.0.0.1:8000",
        "description": "Entorno local de Fixture 2030",
    }
]

schema["info"]["x-generated-at"] = generated_at

json_path = OPENAPI_DIR / "fixture2030-openapi.json"
yaml_path = OPENAPI_DIR / "fixture2030-openapi.yaml"
evidence_path = (
    EVIDENCE_DIR / "11_openapi_exportado.txt"
)

json_path.write_text(
    json.dumps(
        schema,
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

yaml_path.write_text(
    yaml.safe_dump(
        schema,
        allow_unicode=True,
        sort_keys=False,
    ),
    encoding="utf-8",
)

http_methods = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
}

operations = []

for path, definition in schema["paths"].items():
    for method in definition:
        if method.lower() in http_methods:
            operations.append(
                f"{method.upper():6} {path}"
            )

evidence_lines = [
    "=== HITO 10 - CONTRATO OPENAPI ===",
    f"Fecha de ejecucion: {generated_at}",
    f"Titulo: {schema['info']['title']}",
    f"Version API: {schema['info']['version']}",
    f"Version OpenAPI: {schema['openapi']}",
    f"Cantidad de rutas: {len(schema['paths'])}",
    f"Cantidad de operaciones: {len(operations)}",
    "",
    "=== OPERACIONES DOCUMENTADAS ===",
    *sorted(operations),
    "",
    "=== ARCHIVOS GENERADOS ===",
    str(json_path),
    str(yaml_path),
]

evidence = "\n".join(evidence_lines) + "\n"

evidence_path.write_text(
    evidence,
    encoding="utf-8",
)

print(evidence)
print(f"Evidencia: {evidence_path}")
