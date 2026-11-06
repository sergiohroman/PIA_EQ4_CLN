"""Exporta el contrato OpenAPI a docs/api/openapi.json."""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.api.main import create_app  # noqa: E402

destino = RAIZ / "docs" / "api" / "openapi.json"
destino.parent.mkdir(parents=True, exist_ok=True)
esquema = create_app("sqlite://").openapi()
destino.write_text(json.dumps(esquema, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OpenAPI escrito en {destino} ({len(esquema['paths'])} rutas)")
