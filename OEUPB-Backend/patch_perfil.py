path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\directorio_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "def obtener_perfil_egresado(documento: str, db: Session = Depends(get_db)):",
    "def obtener_perfil_egresado(documento: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    mediciones = db.query(Medicion).filter(Medicion.egresado_documento == documento).order_by(Medicion.momento).all()",
    """    med_query = db.query(Medicion).filter(Medicion.egresado_documento == documento)
    if current_user.get('rol') == 'Coordinador_Sede':
        med_query = med_query.filter(Medicion.sede_id == current_user.get('sede_id'))
    mediciones = med_query.order_by(Medicion.momento).all()
    
    if not mediciones and current_user.get('rol') == 'Coordinador_Sede':
        raise HTTPException(status_code=403, detail="No tiene permisos para ver este egresado")
"""
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("directorio_router perfil actualizado.")
