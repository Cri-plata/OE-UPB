path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\usuarios_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Update get_usuarios to hide Admin_CTIC for EVERYONE
old_get = """    from sqlalchemy import or_
    if current_user.get('rol') == 'Coordinador_Sede':
        # Un coordinador no puede ver al CTIC, y solo puede ver a usuarios de su misma sede o usuarios nacionales (Directivos sin sede)
        query = query.filter(Usuario.rol != 'Admin_CTIC')
        query = query.filter(or_(Usuario.sede_id == current_user.get('sede_id'), Usuario.sede_id == None))"""

new_get = """    from sqlalchemy import or_
    # Nadie ve al CTIC en la tabla, ni siquiera el mismo CTIC
    query = query.filter(Usuario.rol != 'Admin_CTIC')
    
    if current_user.get('rol') == 'Coordinador_Sede':
        # Un coordinador solo puede ver a usuarios de su misma sede o usuarios nacionales (Directivos sin sede)
        query = query.filter(or_(Usuario.sede_id == current_user.get('sede_id'), Usuario.sede_id == None))"""

content = content.replace(old_get, new_get)

# Enforce Admin_CTIC can ONLY create Coordinador_Sede
old_create = """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Coordinador_Sede':"""

new_create = """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Admin_CTIC':
        if user_data.rol != 'Coordinador_Sede':
            raise HTTPException(status_code=403, detail="El Administrador CTIC solo tiene permitido crear cuentas de Coordinador de Sede")
            
    if current_user.get('rol') == 'Coordinador_Sede':"""

content = content.replace(old_create, new_create)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Backend actualizado con las nuevas reglas estrictas para CTIC.")
