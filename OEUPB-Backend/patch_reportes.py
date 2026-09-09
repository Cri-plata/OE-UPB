path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\reportes_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "def obtener_kpis(db: Session = Depends(get_db)):",
    "def obtener_kpis(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

# In reportes_router, we query Medicion and Egresado.
content = content.replace(
    "    total_egresados = db.query(Egresado).count()",
    """    query_med = db.query(Medicion)
    if current_user.get('rol') == 'Coordinador_Sede':
        query_med = query_med.filter(Medicion.sede_id == current_user.get('sede_id'))
    
    # El total de egresados debe ser aquellos que estn en mediciones de esta sede
    if current_user.get('rol') == 'Coordinador_Sede':
        total_egresados = db.query(Egresado).join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id')).distinct().count()
    else:
        total_egresados = db.query(Egresado).count()
"""
)

# And replace `mediciones = db.query(Medicion).all()`
content = content.replace(
    "    mediciones = db.query(Medicion).all()",
    "    mediciones = query_med.all()"
)

if "get_current_user" not in content[:500]:
    content = content.replace("from infrastructure.database import get_db", "from infrastructure.database import get_db\nfrom application.auth_service import get_current_user")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("reportes_router actualizado.")
