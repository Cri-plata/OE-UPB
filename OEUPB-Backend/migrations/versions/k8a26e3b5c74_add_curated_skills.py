"""add curated skills catalog

Revision ID: k8a26e3b5c74
Revises: j7f15d2a4b63
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "k8a26e3b5c74"
down_revision: Union[str, Sequence[str], None] = "j7f15d2a4b63"
branch_labels = None
depends_on = None

TABLA = "habilidades_curadas"
RESTRICCIONES = {
    "ck_habilidades_curadas_tipo": "tipo IN ('blanda', 'dura')",
    "ck_habilidades_curadas_estado": "estado IN ('aprobada', 'descartada')",
}


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(TABLA):
        op.create_table(
            TABLA,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("termino_original", sa.String(length=100), nullable=False),
            sa.Column("etiqueta_canonica", sa.String(length=100), nullable=False),
            sa.Column("tipo", sa.String(length=20), nullable=False),
            sa.Column("variantes", sa.JSON(), nullable=False),
            sa.Column("estado", sa.String(length=20), nullable=False),
            sa.Column("creado_por_id", sa.Integer(), nullable=False),
            sa.Column("creado_por_correo", sa.String(length=100), nullable=False),
            sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("termino_original", name="uq_habilidad_curada_termino"),
            sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"], name="fk_habilidades_curadas_usuario"),
            *(sa.CheckConstraint(condicion, name=nombre) for nombre, condicion in RESTRICCIONES.items()),
        )
        op.create_index("ix_habilidades_curadas_id", TABLA, ["id"])
        op.create_index("ix_habilidades_curadas_termino_original", TABLA, ["termino_original"])
        return

    # La tabla pudo crearse antes con Base.metadata.create_all, sin las restricciones CHECK.
    existentes = {restriccion["name"] for restriccion in inspector.get_check_constraints(TABLA)}
    for nombre, condicion in RESTRICCIONES.items():
        if nombre not in existentes:
            op.create_check_constraint(nombre, TABLA, condicion)


def downgrade() -> None:
    op.drop_table(TABLA)
