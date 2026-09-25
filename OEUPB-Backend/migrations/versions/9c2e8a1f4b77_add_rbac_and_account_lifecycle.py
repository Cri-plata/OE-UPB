"""add rbac permissions and account lifecycle

Revision ID: 9c2e8a1f4b77
Revises: d79d5aa142f7
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9c2e8a1f4b77"
down_revision: Union[str, Sequence[str], None] = "d79d5aa142f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("version_autorizacion", sa.Integer(), nullable=False, server_default="1"))
        batch_op.add_column(sa.Column("etiqueta", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("permisos", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("programas", sa.JSON(), nullable=True))

    usuarios = sa.table(
        "usuarios",
        sa.column("permisos", sa.JSON()),
        sa.column("programas", sa.JSON()),
    )
    op.get_bind().execute(usuarios.update().values(permisos=[], programas=[]))
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.alter_column("permisos", existing_type=sa.JSON(), nullable=False)
        batch_op.alter_column("programas", existing_type=sa.JSON(), nullable=False)

    # Los roles heredados de lectura convergen en el único rol técnico aprobado.
    op.execute(
        sa.text(
            "UPDATE usuarios SET rol = 'Usuario_Consulta' "
            "WHERE rol NOT IN ('Admin_CTIC', 'Coordinador_Sede')"
        )
    )

    op.create_table(
        "auditoria_cuentas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("accion", sa.String(length=30), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("actor_correo", sa.String(length=100), nullable=False),
        sa.Column("objetivo_id", sa.Integer(), nullable=False),
        sa.Column("objetivo_correo", sa.String(length=100), nullable=False),
        sa.Column("objetivo_rol", sa.String(length=50), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=True),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auditoria_cuentas_id", "auditoria_cuentas", ["id"])


def downgrade() -> None:
    op.drop_index("ix_auditoria_cuentas_id", table_name="auditoria_cuentas")
    op.drop_table("auditoria_cuentas")
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("programas")
        batch_op.drop_column("permisos")
        batch_op.drop_column("etiqueta")
        batch_op.drop_column("version_autorizacion")
        batch_op.drop_column("activo")
