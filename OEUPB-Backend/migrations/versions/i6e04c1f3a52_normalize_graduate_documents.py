"""normalize graduate identity documents

Revision ID: i6e04c1f3a52
Revises: h5d93b0e2f41
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

from application.documentos import normalizar_documento

revision: str = "i6e04c1f3a52"
down_revision: Union[str, Sequence[str], None] = "h5d93b0e2f41"
branch_labels = None
depends_on = None

TABLAS_REFERENCIADAS = ("mediciones", "egresados_sedes", "auditoria_egresados")


def calcular_cambios(documentos: list[str]) -> dict[str, str]:
    """Mapa documento actual -> normalizado; falla si dos documentos colisionan."""
    existentes = set(documentos)
    cambios = {}
    destinos: dict[str, str] = {}
    for documento in documentos:
        nuevo = normalizar_documento(documento) or documento
        if nuevo in destinos or (nuevo != documento and nuevo in existentes):
            raise RuntimeError(
                "La normalización fusionaría egresados distintos en un mismo documento. "
                "Resuelva los duplicados manualmente antes de aplicar esta migración."
            )
        destinos[nuevo] = documento
        if nuevo != documento:
            cambios[documento] = nuevo
    return cambios


def upgrade() -> None:
    # ETL-01: aplica a los datos existentes la misma normalización que las cargas nuevas.
    bind = op.get_bind()
    documentos = [fila[0] for fila in bind.execute(sa.text("SELECT numero_documento FROM egresados"))]
    cambios = calcular_cambios(documentos)
    if not cambios:
        return
    mysql = bind.dialect.name == "mysql"
    if mysql:
        # Las FK no tienen ON UPDATE CASCADE; se actualizan todas las tablas en la misma transacción.
        bind.execute(sa.text("SET FOREIGN_KEY_CHECKS = 0"))
    try:
        for anterior, nuevo in cambios.items():
            parametros = {"anterior": anterior, "nuevo": nuevo}
            bind.execute(sa.text("UPDATE egresados SET numero_documento = :nuevo WHERE numero_documento = :anterior"), parametros)
            for tabla in TABLAS_REFERENCIADAS:
                bind.execute(sa.text(f"UPDATE {tabla} SET egresado_documento = :nuevo WHERE egresado_documento = :anterior"), parametros)
    finally:
        if mysql:
            bind.execute(sa.text("SET FOREIGN_KEY_CHECKS = 1"))


def downgrade() -> None:
    # Irreversible: el formato original de cada documento no se conserva.
    pass
