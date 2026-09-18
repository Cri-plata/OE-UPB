path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\usuarios_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Update get_usuarios
old_get = """    if current_user.get('rol') == 'Coordinador_Sede':
        # Un coordinador no puede ver al CTIC, solo a su misma sede o directivos/profesores
        query = query.filter(Usuario.rol != 'Admin_CTIC')"""

new_get = """    from sqlalchemy import or_
    if current_user.get('rol') == 'Coordinador_Sede':
        # Un coordinador no puede ver al CTIC, y solo puede ver a usuarios de su misma sede o usuarios nacionales (Directivos sin sede)
        query = query.filter(Usuario.rol != 'Admin_CTIC')
        query = query.filter(or_(Usuario.sede_id == current_user.get('sede_id'), Usuario.sede_id == None))"""

content = content.replace(old_get, new_get)

# Update create_usuario to enforce they can only create for their own sede or national
old_create = """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Coordinador_Sede' and user_data.rol == 'Admin_CTIC':
        raise HTTPException(status_code=403, detail="No tienes permisos para crear un Administrador CTIC")"""

new_create = """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Coordinador_Sede':
        if user_data.rol == 'Admin_CTIC':
            raise HTTPException(status_code=403, detail="No tienes permisos para crear un Administrador CTIC")
        
        # Mapeo temporal para saber si intenta crear en otra sede
        mapa_sedes_verif = {"Bucaramanga": 1, "Medelln": 2, "Palmira": 3, "Montera": 4, "Bogot": 5}
        sede_intentada = mapa_sedes_verif.get(user_data.sede) if user_data.sede else None
        
        # Si intenta asignarle una sede y esa sede NO es la suya
        if sede_intentada and sede_intentada != current_user.get('sede_id'):
            raise HTTPException(status_code=403, detail="Solo puedes crear usuarios para tu propia sede o de nivel Nacional")"""

content = content.replace(old_create, new_create)

# Update delete_usuario
old_delete = """    # Regla de negocio: No se puede eliminar al admin principal
    if usuario.rol == 'Admin_CTIC':
        raise HTTPException(status_code=403, detail="No se puede eliminar al Administrador Principal")"""

new_delete = """    # Regla de negocio: No se puede eliminar al admin principal
    if usuario.rol == 'Admin_CTIC':
        raise HTTPException(status_code=403, detail="No se puede eliminar al Administrador Principal")
    
    if current_user.get('rol') == 'Coordinador_Sede':
        if usuario.sede_id is not None and usuario.sede_id != current_user.get('sede_id'):
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar a un usuario de otra sede")"""

content = content.replace(
    "def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):",
    "def delete_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(old_delete, new_delete)


with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Filtros de Sede mejorados en usuarios_router.")
