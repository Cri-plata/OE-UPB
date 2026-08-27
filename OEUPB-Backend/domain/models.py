from sqlalchemy import Column, Integer, String, Boolean
from infrastructure.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    contrasena_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False) # 'Admin_CTIC', 'Coordinador_Sede', 'Directivo'
    sede_id = Column(Integer, nullable=True) # Nullable porque Admin_CTIC no tiene sede

from sqlalchemy import JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class Egresado(Base):
    __tablename__ = "egresados"
    
    numero_documento = Column(String(50), primary_key=True, index=True)
    primer_nombre = Column(String(100))
    primer_apellido = Column(String(100), nullable=True)
    programa = Column(String(150))
    fecha_grado = Column(DateTime, nullable=True)
    
    mediciones = relationship("Medicion", back_populates="egresado")

class Medicion(Base):
    __tablename__ = "mediciones"
    
    id = Column(Integer, primary_key=True, index=True)
    egresado_documento = Column(String(50), ForeignKey("egresados.numero_documento"))
    momento = Column(Integer) # 0, 1, o 5
    sede_id = Column(Integer) # Sede del coordinador
    respuestas = Column(JSON) # Aquí guardamos las 90+ columnas del Excel dinámicamente
    
    egresado = relationship("Egresado", back_populates="mediciones")
