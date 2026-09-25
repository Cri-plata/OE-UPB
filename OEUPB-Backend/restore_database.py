"""Restaura un respaldo lógico solo con confirmación explícita del nombre de la base."""
import argparse
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import make_url


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True, type=Path)
    parser.add_argument("--confirm-database", required=True)
    args = parser.parse_args()
    load_dotenv(Path(__file__).with_name(".env"))
    url = make_url(os.environ["DATABASE_URL"])
    backup = args.backup.resolve(strict=True)
    if backup.suffix.lower() != ".sql" or args.confirm_database != url.database:
        raise RuntimeError("El archivo o la confirmación de base de datos no son válidos")
    entorno = os.environ.copy()
    entorno["MYSQL_PWD"] = url.password or ""
    comando = ["mysql", "--host", url.host or "localhost", "--port", str(url.port or 3306), "--user", url.username or "", url.database or ""]
    with backup.open("rb") as entrada:
        subprocess.run(comando, stdin=entrada, env=entorno, check=True)
    print(f"restaurado={backup}")


if __name__ == "__main__":
    main()
