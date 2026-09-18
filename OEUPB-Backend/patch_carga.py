path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace endpoint parameters and hardcoded sede
content = content.replace(
    "def procesar_excel(\n    momento: int = Form(...),\n    anio: int = Form(...),\n    file: UploadFile = File(...),\n    db: Session = Depends(get_db)\n):",
    "def procesar_excel(\n    momento: int = Form(...),\n    anio: int = Form(...),\n    file: UploadFile = File(...),\n    db: Session = Depends(get_db),\n    current_user: dict = Depends(get_current_user)\n):"
)

# Historial endpoint
content = content.replace(
    "def obtener_historial_cargas(db: Session = Depends(get_db)):",
    "def obtener_historial_cargas(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)
content = content.replace(
    "    cargas = db.query(Medicion.momento, Medicion.anio, func.count(Medicion.id).label('total'))\\",
    "    query = db.query(Medicion.momento, Medicion.anio, func.count(Medicion.id).label('total'))\n    if current_user.get('rol') == 'Coordinador_Sede':\n        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))\n    cargas = query\\"
)

# Eliminar endpoint
content = content.replace(
    "def eliminar_momento(momento: int, anio: int, db: Session = Depends(get_db)):",
    "def eliminar_momento(momento: int, anio: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):"
)
content = content.replace(
    "    query = db.query(Medicion).filter(Medicion.momento == momento)",
    "    query = db.query(Medicion).filter(Medicion.momento == momento)\n    if current_user.get('rol') == 'Coordinador_Sede':\n        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))"
)

# Replace hardcoded sede in procesar_excel
content = content.replace(
    "    # Extraemos la sede (hardcodeada a 1 por ahora, luego vendrá del token JWT)\n    sede_coordinador = 1",
    "    # Extraemos la sede del token JWT\n    sede_coordinador = current_user.get('sede_id') or 1"
)

# Needs to import get_current_user
if "get_current_user" not in content[:500]:
    content = content.replace("from infrastructure.database import get_db", "from infrastructure.database import get_db\nfrom application.auth_service import get_current_user")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("carga_router actualizado.")
