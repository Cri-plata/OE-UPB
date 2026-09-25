"""Crea un respaldo SQL lógico de la base configurada en DATABASE_URL.

El archivo se guarda fuera del repositorio, en el directorio temporal del sistema.
No imprime credenciales ni contenido de las tablas.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from sqlalchemy.engine import make_url


def quote_identifier(value: str) -> str:
    return f"`{value.replace('`', '``')}`"


def main() -> None:
    load_dotenv(Path(__file__).with_name(".env"))
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL no está configurada")

    url = make_url(database_url)
    if not url.database:
        raise RuntimeError("DATABASE_URL no especifica una base de datos")

    backup_dir = Path(tempfile.gettempdir()) / "oeupb-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = backup_dir / f"{url.database}-pre-alembic-{timestamp}.sql"

    connection = pymysql.connect(
        host=url.host or "localhost",
        port=url.port or 3306,
        user=url.username,
        password=url.password or "",
        database=url.database,
        charset="utf8mb4",
        autocommit=False,
    )

    try:
        with connection.cursor() as cursor, output_path.open("w", encoding="utf-8", newline="\n") as dump:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            cursor.execute("START TRANSACTION WITH CONSISTENT SNAPSHOT")
            cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
            tables = sorted(row[0] for row in cursor.fetchall())

            dump.write("SET NAMES utf8mb4;\nSET FOREIGN_KEY_CHECKS=0;\n\n")
            for table in tables:
                table_id = quote_identifier(table)
                cursor.execute(f"SHOW CREATE TABLE {table_id}")
                create_table = cursor.fetchone()[1]
                dump.write(f"DROP TABLE IF EXISTS {table_id};\n{create_table};\n\n")

                cursor.execute(f"SELECT * FROM {table_id}")
                columns = [quote_identifier(column[0]) for column in cursor.description]
                column_list = ", ".join(columns)
                while rows := cursor.fetchmany(500):
                    values = []
                    for row in rows:
                        escaped = ", ".join(connection.escape(value) for value in row)
                        values.append(f"({escaped})")
                    dump.write(
                        f"INSERT INTO {table_id} ({column_list}) VALUES\n"
                        + ",\n".join(values)
                        + ";\n"
                    )
                dump.write("\n")

            dump.write("SET FOREIGN_KEY_CHECKS=1;\n")
            connection.rollback()
    except Exception:
        output_path.unlink(missing_ok=True)
        raise
    finally:
        connection.close()

    if output_path.stat().st_size == 0:
        raise RuntimeError("El respaldo generado está vacío")

    digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
    print(f"respaldo={output_path}")
    print(f"tamano_bytes={output_path.stat().st_size}")
    print(f"sha256={digest}")


if __name__ == "__main__":
    main()
