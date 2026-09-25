"""baseline existing schema

Revision ID: 70dad5413f5b
Revises: 
Create Date: 2026-09-23 01:55:16.518728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70dad5413f5b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the schema that existed before formal migrations were adopted."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("correo", sa.String(length=100), nullable=False),
        sa.Column("contrasena_hash", sa.String(length=255), nullable=False),
        sa.Column("rol", sa.String(length=50), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_id", "usuarios", ["id"])
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"], unique=True)

    op.create_table(
        "egresados",
        sa.Column("numero_documento", sa.String(length=50), nullable=False),
        sa.Column("primer_nombre", sa.String(length=100), nullable=True),
        sa.Column("primer_apellido", sa.String(length=100), nullable=True),
        sa.Column("programa", sa.String(length=150), nullable=True),
        sa.Column("fecha_grado", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("numero_documento"),
    )
    op.create_index(
        "ix_egresados_numero_documento",
        "egresados",
        ["numero_documento"],
    )

    op.create_table(
        "mediciones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("egresado_documento", sa.String(length=50), nullable=True),
        sa.Column("momento", sa.Integer(), nullable=True),
        sa.Column("anio", sa.Integer(), nullable=True),
        sa.Column("sede_id", sa.Integer(), nullable=True),
        sa.Column("respuestas", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["egresado_documento"],
            ["egresados.numero_documento"],
            name="fk_mediciones_egresados",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mediciones_id", "mediciones", ["id"])


def downgrade() -> None:
    """Remove the baseline schema."""
    op.drop_index("ix_mediciones_id", table_name="mediciones")
    op.drop_table("mediciones")
    op.drop_index("ix_egresados_numero_documento", table_name="egresados")
    op.drop_table("egresados")
    op.drop_index("ix_usuarios_correo", table_name="usuarios")
    op.drop_index("ix_usuarios_id", table_name="usuarios")
    op.drop_table("usuarios")
