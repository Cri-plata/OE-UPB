"""harden temporary credentials

Revision ID: g4c82a9d1e30
Revises: f3b91d7c6a20
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "g4c82a9d1e30"
down_revision: Union[str, Sequence[str], None] = "f3b91d7c6a20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("credencial_temporal_expira_en", sa.DateTime(), nullable=True))
    op.execute(
        "UPDATE usuarios SET credencial_temporal_expira_en = DATE_ADD(UTC_TIMESTAMP(), INTERVAL 24 HOUR) "
        "WHERE debe_cambiar_contrasena = 1"
    )


def downgrade() -> None:
    op.drop_column("usuarios", "credencial_temporal_expira_en")
