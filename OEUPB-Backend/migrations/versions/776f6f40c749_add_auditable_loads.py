"""add auditable loads

Revision ID: 776f6f40c749
Revises: 70dad5413f5b
Create Date: 2026-09-23 01:56:39.063339

"""
from typing import Sequence, Union
from datetime import datetime, timezone
import hashlib

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '776f6f40c749'
down_revision: Union[str, Sequence[str], None] = '70dad5413f5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cargas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre_archivo", sa.String(length=255), nullable=False),
        sa.Column("hash_archivo", sa.String(length=64), nullable=False),
        sa.Column("fecha_carga", sa.DateTime(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("momento", sa.Integer(), nullable=False),
        sa.Column("anio_grado", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=30), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("registros", sa.Integer(), nullable=False),
        sa.Column("errores", sa.JSON(), nullable=True),
        sa.Column("reemplaza_carga_id", sa.Integer(), nullable=True),
        sa.CheckConstraint("momento IN (0, 1, 5)", name="ck_cargas_momento"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["reemplaza_carga_id"], ["cargas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cargas_id", "cargas", ["id"])
    op.create_index(
        "ix_cargas_alcance",
        "cargas",
        ["sede_id", "momento", "anio_grado", "estado"],
    )

    with op.batch_alter_table("mediciones") as batch_op:
        batch_op.add_column(sa.Column("carga_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_mediciones_carga_id", ["carga_id"])
        batch_op.create_foreign_key(
            "fk_mediciones_cargas",
            "cargas",
            ["carga_id"],
            ["id"],
        )

    # Agrupa datos históricos completos en cargas sintéticas. Los registros que
    # carezcan de sede, momento o año permanecen sin carga para revisión manual.
    bind = op.get_bind()
    mediciones = sa.table(
        "mediciones",
        sa.column("id", sa.Integer()),
        sa.column("carga_id", sa.Integer()),
        sa.column("sede_id", sa.Integer()),
        sa.column("momento", sa.Integer()),
        sa.column("anio", sa.Integer()),
    )
    cargas = sa.table(
        "cargas",
        sa.column("id", sa.Integer()),
        sa.column("nombre_archivo", sa.String()),
        sa.column("hash_archivo", sa.String()),
        sa.column("fecha_carga", sa.DateTime()),
        sa.column("usuario_id", sa.Integer()),
        sa.column("sede_id", sa.Integer()),
        sa.column("momento", sa.Integer()),
        sa.column("anio_grado", sa.Integer()),
        sa.column("estado", sa.String()),
        sa.column("version", sa.Integer()),
        sa.column("registros", sa.Integer()),
        sa.column("errores", sa.JSON()),
        sa.column("reemplaza_carga_id", sa.Integer()),
    )
    grupos = bind.execute(
        sa.select(
            mediciones.c.sede_id,
            mediciones.c.momento,
            mediciones.c.anio,
            sa.func.count(mediciones.c.id).label("registros"),
        )
        .where(
            mediciones.c.sede_id.is_not(None),
            mediciones.c.momento.in_([0, 1, 5]),
            mediciones.c.anio.is_not(None),
        )
        .group_by(
            mediciones.c.sede_id,
            mediciones.c.momento,
            mediciones.c.anio,
        )
    ).mappings()

    for grupo in grupos:
        nombre = (
            f"legacy-s{grupo['sede_id']}-m{grupo['momento']}-"
            f"a{grupo['anio']}"
        )
        resultado = bind.execute(
            cargas.insert().values(
                nombre_archivo=nombre,
                hash_archivo=hashlib.sha256(nombre.encode("utf-8")).hexdigest(),
                fecha_carga=datetime.now(timezone.utc).replace(tzinfo=None),
                usuario_id=None,
                sede_id=grupo["sede_id"],
                momento=grupo["momento"],
                anio_grado=grupo["anio"],
                estado="vigente",
                version=1,
                registros=grupo["registros"],
                errores=None,
                reemplaza_carga_id=None,
            )
        )
        carga_id = resultado.lastrowid
        bind.execute(
            mediciones.update()
            .where(
                mediciones.c.sede_id == grupo["sede_id"],
                mediciones.c.momento == grupo["momento"],
                mediciones.c.anio == grupo["anio"],
            )
            .values(carga_id=carga_id)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("mediciones") as batch_op:
        batch_op.drop_constraint("fk_mediciones_cargas", type_="foreignkey")
        batch_op.drop_index("ix_mediciones_carga_id")
        batch_op.drop_column("carga_id")
    op.drop_index("ix_cargas_alcance", table_name="cargas")
    op.drop_index("ix_cargas_id", table_name="cargas")
    op.drop_table("cargas")
