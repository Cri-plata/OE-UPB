"""Comprueba las fronteras de capas, guards y tokens visuales del frontend."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "OEUPB-Frontend" / "src" / "app"
PRESENTATION = APP / "presentation"
STYLES = ROOT / "OEUPB-Frontend" / "src" / "styles.scss"
ROUTES = APP / "app.routes.ts"


def main() -> int:
    errors: list[str] = []
    for source in PRESENTATION.rglob("*.ts"):
        if source.name.endswith(".spec.ts"):
            continue
        content = source.read_text(encoding="utf-8-sig")
        if "HttpClient" in content or "API_BASE_URL" in content:
            errors.append(f"Presentation consume HTTP directamente: {source.relative_to(ROOT)}")

    colors: Counter[str] = Counter()
    for stylesheet in PRESENTATION.rglob("*.scss"):
        colors.update(
            color.lower()
            for color in re.findall(r"#[0-9a-fA-F]{3,8}\b", stylesheet.read_text(encoding="utf-8-sig"))
        )
    repeated = sorted(color for color, count in colors.items() if count > 1)
    if repeated:
        errors.append("Colores hexadecimales repetidos fuera de tokens: " + ", ".join(repeated))

    global_styles = STYLES.read_text(encoding="utf-8-sig")
    for token in ("--color-brand", "--color-background", "--color-surface", "--color-text", "--color-border"):
        if token not in global_styles:
            errors.append(f"Falta token global: {token}")

    routes = ROUTES.read_text(encoding="utf-8-sig")
    if "rolesGuard" not in routes or "authGuard" not in routes or "guestGuard" not in routes:
        errors.append("Las rutas no declaran todos los guards de sesión y rol")

    if errors:
        print("Validación de arquitectura frontend fallida:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Arquitectura frontend válida: capas, guards y tokens verificados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
