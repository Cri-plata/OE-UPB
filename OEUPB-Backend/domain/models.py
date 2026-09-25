from sqlalchemy import Column, Integer, String, Boolean
from infrastructure.database import Base
from sqlalchemy import JSON, ForeignKey, DateTime, Text
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, Index, UniqueConstraint


class Sede(Base):
    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False, unique=True)
    activa = Column(Boolean, nullable=False, default=True)

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        Index("ix_usuarios_correo", "correo", unique=True),
        CheckConstraint("rol = 'Admin_CTIC' OR sede_id IS NOT NULL", name="ck_usuarios_sede_por_rol"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False) # Admin_CTIC, Coordinador_Sede, Usuario_Consulta
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=True)
    debe_cambiar_contrasena = Column(Boolean, nullable=False, default=False)
    credencial_temporal_expira_en = Column(DateTime, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    version_autorizacion = Column(Integer, nullable=False, default=1)
    etiqueta = Column(String(30), nullable=True)
    permisos = Column(JSON, nullable=False, default=list)
    programas = Column(JSON, nullable=False, default=list)

from sqlalchemy.orm import relationship

class Egresado(Base):
    __tablename__ = "egresados"
    
    numero_documento = Column(String(50), primary_key=True, index=True)
    primer_nombre = Column(String(100))
    primer_apellido = Column(String(100), nullable=True)
    programa = Column(String(150))
    fecha_grado = Column(DateTime, nullable=True)
    
    mediciones = relationship("Medicion", back_populates="egresado")


class EgresadoSede(Base):
    __tablename__ = "egresados_sedes"
    __table_args__ = (
        UniqueConstraint("egresado_documento", "sede_id", name="uq_egresado_sede"),
    )

    id = Column(Integer, primary_key=True, index=True)
    egresado_documento = Column(String(50), ForeignKey("egresados.numero_documento"), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class AuditoriaEgresado(Base):
    __tablename__ = "auditoria_egresados"

    id = Column(Integer, primary_key=True, index=True)
    accion = Column(String(20), nullable=False)
    actor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    actor_correo = Column(String(100), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    egresado_documento = Column(String(50), nullable=False)
    cambios = Column(JSON, nullable=False)
    motivo = Column(Text, nullable=False)
    fecha = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

class Medicion(Base):
    __tablename__ = "mediciones"
    __table_args__ = (
        CheckConstraint("momento IN (0, 1, 5)", name="ck_mediciones_momento"),
        UniqueConstraint(
            "egresado_documento", "sede_id", "momento", "anio", "intento",
            name="uq_mediciones_intento_identificado",
        ),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    carga_id = Column(Integer, ForeignKey("cargas.id"), nullable=False, index=True)
    egresado_documento = Column(String(50), ForeignKey("egresados.numero_documento"))
    momento = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    intento = Column(Integer, nullable=False, default=1)
    fecha_registro = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    respuestas = Column(JSON, nullable=False)
    
    egresado = relationship("Egresado", back_populates="mediciones")


class Carga(Base):
    __tablename__ = "cargas"
    __table_args__ = (
        CheckConstraint("momento IN (0, 1, 5)", name="ck_cargas_momento"),
        Index(
            "ix_cargas_alcance",
            "sede_id",
            "momento",
            "anio_grado",
            "estado",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String(255), nullable=False)
    hash_archivo = Column(String(64), nullable=False)
    fecha_carga = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    # Solo puede ser NULL para cargas históricas previas a la auditoría.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    momento = Column(Integer, nullable=False)
    anio_grado = Column(Integer, nullable=False)
    estado = Column(String(30), nullable=False, default="procesando")
    version = Column(Integer, nullable=False, default=1)
    registros = Column(Integer, nullable=False, default=0)
    errores = Column(JSON, nullable=True)
    reemplaza_carga_id = Column(Integer, ForeignKey("cargas.id"), nullable=True)


class AuditoriaCuenta(Base):
    __tablename__ = "auditoria_cuentas"

    id = Column(Integer, primary_key=True, index=True)
    accion = Column(String(30), nullable=False)
    actor_id = Column(Integer, nullable=False)
    actor_correo = Column(String(100), nullable=False)
    objetivo_id = Column(Integer, nullable=False)
    objetivo_correo = Column(String(100), nullable=False)
    objetivo_rol = Column(String(50), nullable=False)
    sede_id = Column(Integer, nullable=True)
    motivo = Column(Text, nullable=False)
    fecha = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class EventoEliminacionCarga(Base):
    __tablename__ = "eventos_eliminacion_carga"

    id = Column(Integer, primary_key=True, index=True)
    carga_id_eliminada = Column(Integer, nullable=False)
    actor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    actor_correo = Column(String(100), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    momento = Column(Integer, nullable=False)
    anio_grado = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False)
    registros = Column(Integer, nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    hash_archivo = Column(String(64), nullable=False)
    motivo = Column(Text, nullable=False)
    fecha = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class PublicacionGrafica(Base):
    __tablename__ = "publicaciones_graficas"
    __table_args__ = (
        UniqueConstraint(
            "sede_id", "grafica_key", "version",
            name="uq_publicaciones_grafica_version",
        ),
        CheckConstraint(
            "estado IN ('publicada', 'retirada', 'reemplazada')",
            name="ck_publicaciones_estado",
        ),
        Index("ix_publicaciones_audiencia", "estado", "sede_id", "permiso_requerido"),
    )

    id = Column(Integer, primary_key=True, index=True)
    grafica_key = Column(String(100), nullable=False)
    titulo = Column(String(180), nullable=False)
    sede_id = Column(Integer, ForeignKey("sedes.id"), nullable=False)
    coordinador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    coordinador_correo = Column(String(100), nullable=False)
    programas = Column(JSON, nullable=False)
    permiso_requerido = Column(String(40), nullable=False)
    definicion = Column(JSON, nullable=False)
    metricas = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False)
    aprobada_privacidad = Column(Boolean, nullable=False)
    estado = Column(String(20), nullable=False, default="publicada")
    fecha_creacion = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    fecha_publicacion = Column(
        DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    fecha_retiro = Column(DateTime, nullable=True)
    retirado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

