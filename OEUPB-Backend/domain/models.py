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
