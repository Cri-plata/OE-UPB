path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\usuarios_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Update create_usuario to block Coordinador_Sede creation by a Coordinador_Sede
old_create_block = """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Coordinador_Sede':
        if user_data.rol == 'Admin_CTIC':
            raise HTTPException(status_code=403, detail="No tienes permisos para crear un Administrador CTIC")"""

new_create_block = """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Coordinador_Sede':
        if user_data.rol == 'Admin_CTIC':
            raise HTTPException(status_code=403, detail="No tienes permisos para crear un Administrador CTIC")
        if user_data.rol == 'Coordinador_Sede':
            raise HTTPException(status_code=403, detail="Un Coordinador de Sede no tiene permisos para crear a otro Coordinador de Sede. (Solicítelo a CTIC)")"""

content = content.replace(old_create_block, new_create_block)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Backend protegido contra creación de coordinadores por coordinadores.")
