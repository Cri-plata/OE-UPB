path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\directorio_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "def obtener_programas_unicos(db: Session = Depends(get_db)):",
    "def obtener_programas_unicos(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    programas = db.query(Egresado.programa).distinct().all()",
    """    query = db.query(Egresado.programa).filter(Egresado.programa != None)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id'))
    programas = query.distinct().all()
"""
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("directorio_router programas arreglado.")
