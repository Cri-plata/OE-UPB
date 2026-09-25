"""Valida convenciones y consumidores del contrato OpenAPI."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "OEUPB-Docs" / "specs" / "api" / "openapi.json"
FRONTEND = ROOT / "OEUPB-Frontend" / "src" / "app"


def main() -> int:
    errors: list[str] = []
    contract = json.loads(OPENAPI.read_text(encoding="utf-8"))
    for path, operations in contract.get("paths", {}).items():
        if path != "/" and not path.startswith("/api/"):
            errors.append(f"Ruta fuera de la convención /api/*: {path}")
        if path.startswith("/api/v1/"):
            errors.append(f"La versión v1 no fue adoptada: {path}")
        for method, operation in operations.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            responses = operation.get("responses", {})
            success_code = next((code for code in responses if code.startswith("2")), None)
            success = responses.get(success_code, {}) if success_code else {}
            schema = next(
                (media.get("schema") for media in success.get("content", {}).values() if media.get("schema")),
                None,
            )
            if path != "/" and not schema:
                errors.append(f"Respuesta exitosa sin esquema: {method.upper()} {path}")

    for source in FRONTEND.rglob("*.ts"):
        content = source.read_text(encoding="utf-8-sig")
        relative = source.relative_to(ROOT)
        if "OEUPB-Contracts" in content:
            errors.append(f"Consumidor aún depende de DTO heredado: {relative}")
        if "http://localhost:8000" in content and "environments" not in source.parts and not source.name.endswith(".spec.ts"):
            errors.append(f"URL de API hardcodeada: {relative}")

    generated = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_api_types.py"), "--check"],
        capture_output=True, text=True,
    )
    if generated.returncode:
        errors.append(generated.stdout.strip() or generated.stderr.strip())

    if errors:
        print("Validación de contratos fallida:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Contratos, tipos y consumidores sincronizados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
