"""add student id to graduates

Revision ID: j7f15d2a4b63
Revises: i6e04c1f3a52
"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from application.documentos import normalizar_documento

revision: str = "j7f15d2a4b63"
down_revision: Union[str, Sequence[str], None] = "i6e04c1f3a52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("egresados", sa.Column("id_estudiante", sa.String(length=30), nullable=True))
    op.create_index("ix_egresados_id_estudiante", "egresados", ["id_estudiante"])

    # Completa el ID con la columna USUARIO de la medición más reciente de cada egresado.
    bind = op.get_bind()
    filas = bind.execute(sa.text(
        "SELECT egresado_documento, respuestas FROM mediciones "
        "WHERE egresado_documento IS NOT NULL ORDER BY fecha_registro, id"
    ))
    ids = {}
    for documento, respuestas in filas:
        if isinstance(respuestas, str):
            respuestas = json.loads(respuestas)
        id_estudiante = normalizar_documento((respuestas or {}).get("USUARIO"))
        if id_estudiante:
            ids[documento] = id_estudiante[:30]
    for documento, id_estudiante in ids.items():
        bind.execute(
            sa.text("UPDATE egresados SET id_estudiante = :id WHERE numero_documento = :documento"),
            {"id": id_estudiante, "documento": documento},
        )


def downgrade() -> None:
    op.drop_index("ix_egresados_id_estudiante", table_name="egresados")
    op.drop_column("egresados", "id_estudiante")
