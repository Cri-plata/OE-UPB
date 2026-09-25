"""harden data model and add catalogs/audit

Revision ID: c4d73f1a8e20
Revises: 9c2e8a1f4b77
"""
from collections import defaultdict
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c4d73f1a8e20"
down_revision: Union[str, Sequence[str], None] = "9c2e8a1f4b77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEDES = (
    {"id": 1, "codigo": "BUC", "nombre": "Bucaramanga", "activa": True},
    {"id": 2, "codigo": "MED", "nombre": "Medellín", "activa": True},
    {"id": 3, "codigo": "PAL", "nombre": "Palmira", "activa": True},
    {"id": 4, "codigo": "MON", "nombre": "Montería", "activa": True},
    {"id": 5, "codigo": "BOG", "nombre": "Bogotá", "activa": True},
)


def upgrade() -> None:
    bind = op.get_bind()
    op.create_table(
        "sedes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=20), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo", name="uq_sedes_codigo"),
        sa.UniqueConstraint("nombre", name="uq_sedes_nombre"),
    )
    sedes = sa.table(
        "sedes", sa.column("id", sa.Integer()), sa.column("codigo", sa.String()),
        sa.column("nombre", sa.String()), sa.column("activa", sa.Boolean()),
    )
    bind.execute(sedes.insert(), list(SEDES))

    incompletas = bind.execute(sa.text(
        "SELECT COUNT(*) FROM mediciones WHERE carga_id IS NULL OR sede_id IS NULL "
        "OR momento IS NULL OR anio IS NULL OR respuestas IS NULL"
    )).scalar_one()
    if incompletas:
        raise RuntimeError(
            f"Existen {incompletas} mediciones históricas incompletas; "
            "deben corregirse antes de aplicar esta migración"
        )

    sedes_invalidas = bind.execute(sa.text(
        "SELECT COUNT(*) FROM ("
        "SELECT sede_id FROM usuarios WHERE sede_id IS NOT NULL "
        "UNION ALL SELECT sede_id FROM cargas "
        "UNION ALL SELECT sede_id FROM mediciones"
        ") alcance WHERE sede_id NOT IN (1,2,3,4,5)"
    )).scalar_one()
    if sedes_invalidas:
        raise RuntimeError(f"Existen {sedes_invalidas} referencias a sedes desconocidas")

    usuarios = sa.table(
        "usuarios", sa.column("id", sa.Integer()), sa.column("nombre", sa.String()),
        sa.column("correo", sa.String()), sa.column("contrasena_hash", sa.String()),
        sa.column("rol", sa.String()), sa.column("sede_id", sa.Integer()),
        sa.column("debe_cambiar_contrasena", sa.Boolean()),
        sa.column("activo", sa.Boolean()), sa.column("version_autorizacion", sa.Integer()),
        sa.column("etiqueta", sa.String()), sa.column("permisos", sa.JSON()),
        sa.column("programas", sa.JSON()),
    )
    correo_sistema = "migracion.historica@upb.edu.co"
    actor_id = bind.execute(
        sa.select(usuarios.c.id).where(usuarios.c.correo == correo_sistema)
    ).scalar_one_or_none()
    if actor_id is None:
        resultado = bind.execute(usuarios.insert().values(
            nombre="Migración histórica", correo=correo_sistema,
            contrasena_hash="!cuenta-tecnica-sin-acceso!", rol="Admin_CTIC",
            sede_id=None, debe_cambiar_contrasena=False, activo=False,
            version_autorizacion=1, etiqueta=None, permisos=[], programas=[],
        ))
        actor_id = resultado.lastrowid
    bind.execute(sa.text(
        "UPDATE cargas SET usuario_id=:actor_id WHERE usuario_id IS NULL"
    ), {"actor_id": actor_id})

    with op.batch_alter_table("mediciones") as batch_op:
        batch_op.add_column(sa.Column("intento", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("fecha_registro", sa.DateTime(), nullable=True))

    filas = bind.execute(sa.text(
        "SELECT id, egresado_documento, sede_id, momento, anio FROM mediciones ORDER BY id"
    )).mappings().all()
    contadores: dict[tuple, int] = defaultdict(int)
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    for fila in filas:
        clave = (
            ("anonimo", fila["id"]) if fila["egresado_documento"] is None else
            (fila["egresado_documento"], fila["sede_id"], fila["momento"], fila["anio"])
        )
        contadores[clave] += 1
        bind.execute(
            sa.text("UPDATE mediciones SET intento=:intento, fecha_registro=:fecha WHERE id=:id"),
            {"intento": contadores[clave], "fecha": ahora, "id": fila["id"]},
        )

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.create_foreign_key("fk_usuarios_sede", "sedes", ["sede_id"], ["id"])
    with op.batch_alter_table("cargas") as batch_op:
        batch_op.alter_column("usuario_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key("fk_cargas_sede", "sedes", ["sede_id"], ["id"])
    with op.batch_alter_table("mediciones") as batch_op:
        batch_op.alter_column("carga_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("momento", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("anio", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("sede_id", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("respuestas", existing_type=sa.JSON(), nullable=False)
        batch_op.alter_column("intento", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("fecha_registro", existing_type=sa.DateTime(), nullable=False)
        batch_op.create_foreign_key("fk_mediciones_sede", "sedes", ["sede_id"], ["id"])
        batch_op.create_check_constraint("ck_mediciones_momento", "momento IN (0, 1, 5)")
        batch_op.create_unique_constraint(
            "uq_mediciones_intento_identificado",
            ["egresado_documento", "sede_id", "momento", "anio", "intento"],
        )

    op.create_table(
        "eventos_eliminacion_carga",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("carga_id_eliminada", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("actor_correo", sa.String(length=100), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("momento", sa.Integer(), nullable=False),
        sa.Column("anio_grado", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("registros", sa.Integer(), nullable=False),
        sa.Column("nombre_archivo", sa.String(length=255), nullable=False),
        sa.Column("hash_archivo", sa.String(length=64), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["usuarios.id"], name="fk_evento_carga_actor"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], name="fk_evento_carga_sede"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eventos_eliminacion_carga_id", "eventos_eliminacion_carga", ["id"])


def downgrade() -> None:
    op.drop_index("ix_eventos_eliminacion_carga_id", table_name="eventos_eliminacion_carga")
    op.drop_table("eventos_eliminacion_carga")
    with op.batch_alter_table("mediciones") as batch_op:
        batch_op.drop_constraint("uq_mediciones_intento_identificado", type_="unique")
        batch_op.drop_constraint("ck_mediciones_momento", type_="check")
        batch_op.drop_constraint("fk_mediciones_sede", type_="foreignkey")
        batch_op.alter_column("respuestas", existing_type=sa.JSON(), nullable=True)
        batch_op.alter_column("sede_id", existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column("anio", existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column("momento", existing_type=sa.Integer(), nullable=True)
        batch_op.alter_column("carga_id", existing_type=sa.Integer(), nullable=True)
        batch_op.drop_column("fecha_registro")
        batch_op.drop_column("intento")
    with op.batch_alter_table("cargas") as batch_op:
        batch_op.drop_constraint("fk_cargas_sede", type_="foreignkey")
        batch_op.alter_column("usuario_id", existing_type=sa.Integer(), nullable=True)
    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_constraint("fk_usuarios_sede", type_="foreignkey")
    op.drop_table("sedes")
