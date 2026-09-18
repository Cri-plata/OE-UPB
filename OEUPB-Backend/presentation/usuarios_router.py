from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from infrastructure.database import get_db
from application.auth_service import get_current_user
from application.auth_service import get_password_hash
from domain.models import Usuario
from pydantic import BaseModel
from typing import List, Optional, Union

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

# Contratos (Pydantic Models)
class UsuarioCreateRequest(BaseModel):
    nombre: str
    correo: str
    rol: str
    sede: Optional[str] = None

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: str
    sede_id: Optional[Union[str, int]] = None # En una DB real apuntaría a una tabla Sedes, por ahora pasamos el string

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UsuarioResponse])
def get_usuarios(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Usuario)
    from sqlalchemy import or_
    # Nadie ve al CTIC en la tabla, ni siquiera el mismo CTIC
    query = query.filter(Usuario.rol != 'Admin_CTIC')
    
    if current_user.get('rol') == 'Coordinador_Sede':
        # Un coordinador solo puede ver a usuarios de su misma sede o usuarios nacionales (Directivos sin sede)
        query = query.filter(or_(Usuario.sede_id == current_user.get('sede_id'), Usuario.sede_id == None))
    usuarios = query.all()

    # Mapeo temporal del id de la sede para que el Frontend vea el string
    for u in usuarios:
        if u.sede_id == 1: u.sede_id = "Bucaramanga"
        elif u.sede_id == 2: u.sede_id = "Medellín"
        elif u.sede_id == 3: u.sede_id = "Palmira"
        elif u.sede_id == 4: u.sede_id = "Montería"
        elif u.sede_id == 5: u.sede_id = "Bogotá"
    return usuarios

@router.post("/", response_model=UsuarioResponse)
def create_usuario(user_data: UsuarioCreateRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verificar si el correo ya existe
    if not user_data.correo.endswith('@upb.edu.co'):
        raise HTTPException(status_code=400, detail="El correo debe ser @upb.edu.co")

    existe = db.query(Usuario).filter(Usuario.correo == user_data.correo).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado en el sistema")

    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Admin_CTIC':
        if user_data.rol != 'Coordinador_Sede':
            raise HTTPException(status_code=403, detail="El Administrador CTIC solo tiene permitido crear cuentas de Coordinador de Sede")
            
    if current_user.get('rol') == 'Coordinador_Sede':
        if user_data.rol == 'Admin_CTIC':
            raise HTTPException(status_code=403, detail="No tienes permisos para crear un Administrador CTIC")
        if user_data.rol == 'Coordinador_Sede':
            raise HTTPException(status_code=403, detail="Un Coordinador de Sede no tiene permisos para crear a otro Coordinador de Sede. (Solicítelo a CTIC)")
        
        # Mapeo temporal para saber si intenta crear en otra sede
        mapa_sedes_verif = {"Bucaramanga": 1, "Medelln": 2, "Palmira": 3, "Montera": 4, "Bogot": 5}
        sede_intentada = mapa_sedes_verif.get(user_data.sede) if user_data.sede else None
        
        # Si intenta asignarle una sede y esa sede NO es la suya
        if sede_intentada and sede_intentada != current_user.get('sede_id'):
            raise HTTPException(status_code=403, detail="Solo puedes crear usuarios para tu propia sede o de nivel Nacional")
        
    # Mapeo simple de sedes
    mapa_sedes = {"Bucaramanga": 1, "Medellín": 2, "Palmira": 3, "Montería": 4, "Bogotá": 5}
    sede_id = mapa_sedes.get(user_data.sede) if user_data.sede else None

    nuevo_usuario = Usuario(
        nombre=user_data.nombre,
        correo=user_data.correo,
        contrasena_hash=get_password_hash("upb123"), # Contraseña por defecto
        rol=user_data.rol,
        sede_id=sede_id
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


@router.delete("/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Regla de negocio: No se puede eliminar al admin principal
    if usuario.rol == 'Admin_CTIC':
        raise HTTPException(status_code=403, detail="No se puede eliminar al Administrador Principal")
    
    if current_user.get('rol') == 'Coordinador_Sede':
        if usuario.sede_id is not None and usuario.sede_id != current_user.get('sede_id'):
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar a un usuario de otra sede")
        
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado exitosamente"}

