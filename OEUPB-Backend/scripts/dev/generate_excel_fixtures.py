"""Genera libros Excel sintéticos compatibles con el flujo de carga."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


PROGRAMAS = (
    "Ingeniería de Sistemas",
    "Derecho",
    "Psicología",
    "Arquitectura",
    "Medicina",
)


def generate_fixture(output: Path, rows: int, double_degree_rate: float, seed: int) -> int:
    """Escribe datos ficticios deterministas y devuelve el número de filas."""
    rng = random.Random(seed)
    records: list[dict[str, object]] = []
    for index in range(rows):
        document = 1_000_000_000 + index
        graduation = datetime(2025, 12, 31) - timedelta(days=rng.randint(30, 2_000))
        base = {
            "NUMERO_DOCUMENTO": document,
            "PRIMER NOMBRE": f"Egresado_{index}",
            "PRIMER_APELLIDO": f"Sintetico_{index}",
            "PROGRAMA": rng.choice(PROGRAMAS),
            "FECHA_GRADO": graduation.strftime("%Y-%m-%d %H:%M:%S"),
        }
        records.append(base)
        if double_degree_rate and rng.random() < double_degree_rate:
            records.append({
                **base,
                "PROGRAMA": rng.choice(PROGRAMAS),
                "FECHA_GRADO": (graduation - timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S"),
            })
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_excel(output, index=False)
    return len(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Ruta del archivo .xlsx de salida")
    parser.add_argument("--rows", type=int, default=50, help="Cantidad de egresados sintéticos")
    parser.add_argument("--double-degree-rate", type=float, default=0.05, help="Probabilidad entre 0 y 1 de una titulación anterior")
    parser.add_argument("--seed", type=int, default=20260924, help="Semilla reproducible")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.suffix.lower() != ".xlsx":
        raise SystemExit("La salida debe tener extensión .xlsx")
    if args.rows < 1:
        raise SystemExit("--rows debe ser mayor que cero")
    if not 0 <= args.double_degree_rate <= 1:
        raise SystemExit("--double-degree-rate debe estar entre 0 y 1")
    written = generate_fixture(args.output, args.rows, args.double_degree_rate, args.seed)
    print(f"Archivo generado: {args.output.resolve()} ({written} filas)")


if __name__ == "__main__":
    main()
