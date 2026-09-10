path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\usuarios_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Protect GET and POST
content = content.replace(
    "def get_usuarios(db: Session = Depends(get_db)):",
    "def get_usuarios(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    usuarios = db.query(Usuario).all()",
    """    query = db.query(Usuario)
    if current_user.get('rol') == 'Coordinador_Sede':
        # Un coordinador no puede ver al CTIC, solo a su misma sede o directivos/profesores
        query = query.filter(Usuario.rol != 'Admin_CTIC')
    usuarios = query.all()
"""
)

content = content.replace(
    "def create_usuario(user_data: UsuarioCreateRequest, db: Session = Depends(get_db)):",
    "def create_usuario(user_data: UsuarioCreateRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    # Mapeo simple de sedes",
    """    # Bloquear escalada de privilegios
    if current_user.get('rol') == 'Coordinador_Sede' and user_data.rol == 'Admin_CTIC':
        raise HTTPException(status_code=403, detail="No tienes permisos para crear un Administrador CTIC")
        
    # Mapeo simple de sedes"""
)

if "get_current_user" not in content[:500]:
    content = content.replace("from infrastructure.database import get_db", "from infrastructure.database import get_db\nfrom application.auth_service import get_current_user")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Backend usuarios_router protegido.")
