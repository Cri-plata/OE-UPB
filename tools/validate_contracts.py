"""Valida convenciones y consumidores del contrato OpenAPI."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "OEUPB-Docs" / "specs" / "api" / "openapi.json"
FRONTEND = ROOT / "OEUPB-Frontend" / "src" / "app"
CLIENTES = FRONTEND / "data" / "api"
_BASE_CLIENTE = re.compile(r"url\s*=\s*`\$\{API_BASE_URL\}([^`]*)`")
_PLANTILLA = re.compile(r"`\$\{(API_BASE_URL|this\.url)\}([^`]*)`")
_PARAMETRO_TS = re.compile(r"\$\{[^}]+\}")


def rutas_de_clientes() -> list[tuple[str, str]]:
    """Rutas `/api/...` que construyen los clientes de Data; `*` marca un segmento variable."""
    rutas = []
    for source in sorted(CLIENTES.glob("*.api.ts")):
        content = source.read_text(encoding="utf-8-sig")
        base = _BASE_CLIENTE.search(content)
        prefijo_base = base.group(1) if base else ""
        for linea in content.splitlines():
            if _BASE_CLIENTE.search(linea):
                continue  # Definición de la URL base, no una petición.
            for origen, resto in _PLANTILLA.findall(linea):
                prefijo = "" if origen == "API_BASE_URL" else prefijo_base
                rutas.append((source.name, "/api" + prefijo + _PARAMETRO_TS.sub("*", resto)))
            # `this.url` sin plantilla (p. ej. `http.get(this.url)`) apunta a la base exacta.
            if base and re.search(r"\(this\.url[,)]", linea):
                rutas.append((source.name, "/api" + prefijo_base))
    return rutas


def _coincide(cliente: str, contrato: str) -> bool:
    """Compara segmento a segmento; la barra final cuenta, porque FastAPI redirige (307)."""
    a, b = cliente.split("/"), contrato.split("/")
    return len(a) == len(b) and all(x == y or x == "*" or y.startswith("{") for x, y in zip(a, b))


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

    rutas_contrato = list(contract.get("paths", {}))
    for archivo, ruta in rutas_de_clientes():
        if not any(_coincide(ruta, contrato) for contrato in rutas_contrato):
            errors.append(f"Ruta del cliente sin operación idéntica en OpenAPI (revise la barra final): {archivo} {ruta}")

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
