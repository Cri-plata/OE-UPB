path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\reportes_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "def get_reporte_general(db: Session = Depends(get_db)):",
    "def get_reporte_general(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    total_egresados = db.query(Egresado).count()",
    """    query_med = db.query(Medicion)
    if current_user.get('rol') == 'Coordinador_Sede':
        query_med = query_med.filter(Medicion.sede_id == current_user.get('sede_id'))
    
    if current_user.get('rol') == 'Coordinador_Sede':
        total_egresados = db.query(Egresado).join(Medicion).filter(Medicion.sede_id == current_user.get('sede_id')).distinct().count()
    else:
        total_egresados = db.query(Egresado).count()
"""
)

content = content.replace(
    "    mediciones = db.query(Medicion).all()",
    "    mediciones = query_med.all()"
)

content = content.replace(
    "def get_tendencias(db: Session = Depends(get_db)):",
    "def get_tendencias(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)

content = content.replace(
    "    mediciones = db.query(Medicion).all()",
    """    query_med = db.query(Medicion)
    if current_user.get('rol') == 'Coordinador_Sede':
        query_med = query_med.filter(Medicion.sede_id == current_user.get('sede_id'))
    mediciones = query_med.all()
"""
)

if "get_current_user" not in content[:500]:
    content = content.replace("from infrastructure.database import get_db", "from infrastructure.database import get_db\nfrom application.auth_service import get_current_user")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("reportes_router arreglado y protegido.")
