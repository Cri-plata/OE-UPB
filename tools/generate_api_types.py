"""Genera tipos TypeScript simples desde components.schemas del OpenAPI canónico."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "OEUPB-Docs" / "specs" / "api" / "openapi.json"
OUTPUT = ROOT / "OEUPB-Frontend" / "src" / "app" / "data" / "api" / "generated-api.models.ts"


def ts_type(schema: dict) -> str:
    if "$ref" in schema:
        return schema["$ref"].rsplit("/", 1)[-1]
    if "anyOf" in schema:
        return " | ".join(dict.fromkeys(ts_type(item) for item in schema["anyOf"]))
    if "enum" in schema:
        return " | ".join(json.dumps(value, ensure_ascii=False) for value in schema["enum"])
    kind = schema.get("type")
    if isinstance(kind, list):
        return " | ".join("null" if item == "null" else ts_type({"type": item}) for item in kind)
    if kind == "array":
        return f"Array<{ts_type(schema.get('items', {}))}>"
    if kind == "object":
        if "additionalProperties" in schema:
            value = schema["additionalProperties"]
            return f"Record<string, {ts_type(value) if isinstance(value, dict) else 'unknown'}>"
        return "Record<string, unknown>"
    if kind in ("integer", "number"):
        return "number"
    if kind == "boolean":
        return "boolean"
    if kind == "null":
        return "null"
    if kind == "string":
        return "string"
    return "unknown"


def generate(contract: dict) -> str:
    lines = [
        "// Archivo generado desde OEUPB-Docs/specs/api/openapi.json.",
        "// No editar manualmente; ejecute: npm run generate:api",
        "",
    ]
    for name, schema in sorted(contract.get("components", {}).get("schemas", {}).items()):
        if schema.get("type") != "object" or not schema.get("properties"):
            lines.append(f"export type {name} = {ts_type(schema)};")
            lines.append("")
            continue
        required = set(schema.get("required", []))
        lines.append(f"export interface {name} {{")
        for prop, prop_schema in schema["properties"].items():
            optional = "" if prop in required else "?"
            lines.append(f"  {json.dumps(prop, ensure_ascii=False)}{optional}: {ts_type(prop_schema)};")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = generate(json.loads(OPENAPI.read_text(encoding="utf-8")))
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if actual != expected:
            print("Los tipos TypeScript no están sincronizados con OpenAPI.")
            return 1
        print("Tipos TypeScript sincronizados con OpenAPI.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Tipos generados en {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
