path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix get_historial
old_historial = """@router.get("/historial")
def get_historial(db: Session = Depends(get_db)):
    from sqlalchemy import func
    # Consultar cuntas mediciones hay por cada momento
    resultados = db.query(Medicion.momento, Medicion.anio, func.count(Medicion.id)).group_by(Medicion.momento, Medicion.anio).all()"""

new_historial = """@router.get("/historial")
def get_historial(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    from sqlalchemy import func
    # Filtrar por sede si es coordinador
    query = db.query(Medicion.momento, Medicion.anio, func.count(Medicion.id))
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
    resultados = query.group_by(Medicion.momento, Medicion.anio).all()"""

content = content.replace(old_historial, new_historial)
# If encoding messes up 'cuántas', I'll use regex.
import re
content = re.sub(
    r'@router\.get\("/historial"\)\s*def get_historial\(db: Session = Depends\(get_db\)\):\s*from sqlalchemy import func\s*#.*?\s*resultados = db\.query\(Medicion\.momento, Medicion\.anio, func\.count\(Medicion\.id\)\)\.group_by\(Medicion\.momento,\s*Medicion\.anio\)\.all\(\)',
    """@router.get("/historial")
def get_historial(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    from sqlalchemy import func
    query = db.query(Medicion.momento, Medicion.anio, func.count(Medicion.id))
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
    resultados = query.group_by(Medicion.momento, Medicion.anio).all()""",
    content
)

# Fix eliminar_momento
content = re.sub(
    r'@router\.delete\("/momento/\{momento\}/\{anio\}"\)\s*def eliminar_momento\(momento: int, anio: str, db: Session = Depends\(get_db\)\):',
    """@router.delete("/momento/{momento}/{anio}")
def eliminar_momento(momento: int, anio: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get('rol') == 'Coordinador_Sede':
        # Validar que no borre algo de otra sede? Realmente al borrar vamos a filtrar por sede
        pass""",
    content
)

content = re.sub(
    r'db\.query\(Medicion\)\.filter\(Medicion\.momento == momento,\s*Medicion\.anio\.is_\(None\)\)\.delete\(synchronize_session=False\)',
    """(db.query(Medicion).filter(Medicion.momento == momento, Medicion.anio.is_(None))
       .filter(Medicion.sede_id == current_user.get('sede_id') if current_user.get('rol') == 'Coordinador_Sede' else True)
       .delete(synchronize_session=False))""",
    content
)

content = re.sub(
    r'db\.query\(Medicion\)\.filter\(Medicion\.momento == momento, Medicion\.anio == \s*int\(anio\)\)\.delete\(synchronize_session=False\)',
    """(db.query(Medicion).filter(Medicion.momento == momento, Medicion.anio == int(anio))
       .filter(Medicion.sede_id == current_user.get('sede_id') if current_user.get('rol') == 'Coordinador_Sede' else True)
       .delete(synchronize_session=False))""",
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("carga_router protegido en historial y eliminación.")
