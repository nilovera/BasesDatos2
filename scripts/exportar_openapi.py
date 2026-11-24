import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != ROOT]
sys.path.insert(0, str(ROOT / "backend"))

from app.main import app  # noqa: E402


target = ROOT / "backend" / "openapi.json"
target.write_text(
    json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"OpenAPI exportado en {target}")
