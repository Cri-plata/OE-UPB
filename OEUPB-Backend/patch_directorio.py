path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\directorio_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "    limit: int = Query(50, ge=1, le=100),\n    db: Session = Depends(get_db)\n):",
    "    limit: int = Query(50, ge=1, le=100),\n    db: Session = Depends(get_db),\n    current_user: dict = Depends(get_current_user)\n):"
)

content = content.replace(
    "    query = db.query(Egresado)",
    """    query = db.query(Egresado)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id'))
"""
)

content = content.replace(
    "def obtener_programas(db: Session = Depends(get_db)):",
    "def obtener_programas(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    programas = db.query(Egresado.programa).filter(Egresado.programa != None).distinct().all()",
    """    query = db.query(Egresado.programa).filter(Egresado.programa != None)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id'))
    programas = query.distinct().all()
"""
)

if "get_current_user" not in content[:500]:
    content = content.replace("from infrastructure.database import get_db", "from infrastructure.database import get_db\nfrom application.auth_service import get_current_user")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("directorio_router actualizado.")
