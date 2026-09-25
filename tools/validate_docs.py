"""Validaciones mínimas y sin dependencias para la documentación de OE UPB."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "OEUPB-Docs"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def validate_links() -> list[str]:
    errors: list[str] = []
    for document in DOCS.rglob("*.md"):
        content = document.read_text(encoding="utf-8-sig")
        for match in LINK_RE.finditer(content):
            raw_target = match.group(1).strip()
            target = raw_target.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (document.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{document.relative_to(ROOT)} -> {raw_target}")
    return errors


def validate_openapi() -> list[str]:
    contract = DOCS / "specs" / "api" / "openapi.json"
    try:
        payload = json.loads(contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"No se pudo leer OpenAPI: {exc}"]

    errors: list[str] = []
    if not str(payload.get("openapi", "")).startswith("3."):
        errors.append("OpenAPI debe declarar una versión 3.x")
    paths = payload.get("paths")
    if not isinstance(paths, dict) or not paths:
        errors.append("OpenAPI no contiene rutas")
    elif not all(path.startswith("/") for path in paths):
        errors.append("Todas las rutas OpenAPI deben comenzar con /")
    return errors


def main() -> int:
    errors = validate_links() + validate_openapi()
    if errors:
        print("Validación documental fallida:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Documentación válida: enlaces locales y OpenAPI verificados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

