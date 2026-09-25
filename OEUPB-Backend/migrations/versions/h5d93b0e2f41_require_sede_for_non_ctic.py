"""require sede for non CTIC accounts

Revision ID: h5d93b0e2f41
Revises: g4c82a9d1e30
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "h5d93b0e2f41"
down_revision: Union[str, Sequence[str], None] = "g4c82a9d1e30"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # DB-03: solo Admin_CTIC puede carecer de sede. Se verifica antes de crear la
    # restricción para fallar con un mensaje claro en lugar de un error de MySQL.
    invalidas = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM usuarios WHERE rol <> 'Admin_CTIC' AND sede_id IS NULL")
    ).scalar()
    if invalidas:
        raise RuntimeError(
            f"{invalidas} cuentas no CTIC no tienen sede. Asígneles una sede o desactívelas y "
            "corrija su sede antes de aplicar esta migración."
        )
    op.create_check_constraint(
        "ck_usuarios_sede_por_rol", "usuarios", "rol = 'Admin_CTIC' OR sede_id IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_constraint("ck_usuarios_sede_por_rol", "usuarios", type_="check")
