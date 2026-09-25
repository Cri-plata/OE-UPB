"""add manual graduate registry and audit

Revision ID: f3b91d7c6a20
Revises: e8a4b7c2d901
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f3b91d7c6a20"
down_revision: Union[str, Sequence[str], None] = "e8a4b7c2d901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "egresados_sedes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("egresado_documento", sa.String(50), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("creado_por_id", sa.Integer(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["egresado_documento"], ["egresados.numero_documento"]),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"]),
        sa.ForeignKeyConstraint(["creado_por_id"], ["usuarios.id"]),
        sa.UniqueConstraint("egresado_documento", "sede_id", name="uq_egresado_sede"),
    )
    op.create_index(op.f("ix_egresados_sedes_id"), "egresados_sedes", ["id"])
    op.create_table(
        "auditoria_egresados",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("accion", sa.String(20), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("actor_correo", sa.String(100), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("egresado_documento", sa.String(50), nullable=False),
        sa.Column("cambios", sa.JSON(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"]),
    )
    op.create_index(op.f("ix_auditoria_egresados_id"), "auditoria_egresados", ["id"])


def downgrade() -> None:
    op.drop_table("auditoria_egresados")
    op.drop_table("egresados_sedes")
