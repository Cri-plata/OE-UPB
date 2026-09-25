"""add immutable chart publications

Revision ID: e8a4b7c2d901
Revises: c4d73f1a8e20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8a4b7c2d901"
down_revision: Union[str, Sequence[str], None] = "c4d73f1a8e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "publicaciones_graficas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("grafica_key", sa.String(length=100), nullable=False),
        sa.Column("titulo", sa.String(length=180), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("coordinador_id", sa.Integer(), nullable=False),
        sa.Column("coordinador_correo", sa.String(length=100), nullable=False),
        sa.Column("programas", sa.JSON(), nullable=False),
        sa.Column("permiso_requerido", sa.String(length=40), nullable=False),
        sa.Column("definicion", sa.JSON(), nullable=False),
        sa.Column("metricas", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("aprobada_privacidad", sa.Boolean(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=False),
        sa.Column("fecha_publicacion", sa.DateTime(), nullable=False),
        sa.Column("fecha_retiro", sa.DateTime(), nullable=True),
        sa.Column("retirado_por_id", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "estado IN ('publicada', 'retirada', 'reemplazada')",
            name="ck_publicaciones_estado",
        ),
        sa.ForeignKeyConstraint(["coordinador_id"], ["usuarios.id"], name="fk_publicaciones_coordinador"),
        sa.ForeignKeyConstraint(["retirado_por_id"], ["usuarios.id"], name="fk_publicaciones_retirado_por"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], name="fk_publicaciones_sede"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "sede_id", "grafica_key", "version",
            name="uq_publicaciones_grafica_version",
        ),
    )
    op.create_index(op.f("ix_publicaciones_graficas_id"), "publicaciones_graficas", ["id"], unique=False)
    op.create_index(
        "ix_publicaciones_audiencia",
        "publicaciones_graficas",
        ["estado", "sede_id", "permiso_requerido"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_publicaciones_audiencia", table_name="publicaciones_graficas")
    op.drop_index(op.f("ix_publicaciones_graficas_id"), table_name="publicaciones_graficas")
    op.drop_table("publicaciones_graficas")
