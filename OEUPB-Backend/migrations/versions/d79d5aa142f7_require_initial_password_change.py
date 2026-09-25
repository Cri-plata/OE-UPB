"""require initial password change

Revision ID: d79d5aa142f7
Revises: 776f6f40c749
Create Date: 2026-09-23 12:17:49.100160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd79d5aa142f7'
down_revision: Union[str, Sequence[str], None] = '776f6f40c749'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(
            sa.Column(
                "debe_cambiar_contrasena",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    usuarios = sa.table(
        "usuarios",
        sa.column("debe_cambiar_contrasena", sa.Boolean()),
    )
    op.execute(usuarios.update().values(debe_cambiar_contrasena=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("debe_cambiar_contrasena")
