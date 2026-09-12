path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Extract user sede for the check
# Right now, sede_coordinador is defined LATER in the function!
# We need to extract current_user.get('sede_id') for the duplication check.

old_rule = """    # REGLA DE NEGOCIO: Evitar duplicidad de cargas
    carga_existente = db.query(Medicion).filter(Medicion.momento == momento, Medicion.anio == anio).first()
    if carga_existente:
        raise HTTPException(
            status_code=409, 
            detail=f"Ya existen registros cargados para el Momento {momento} del ao {anio}. Por favor, elimine el archivo desde el Historial antes de volver a cargarlo."
        )"""

new_rule = """    # REGLA DE NEGOCIO: Evitar duplicidad de cargas por sede
    sede_coordinador_actual = current_user.get('sede_id') or 1
    carga_existente = db.query(Medicion).filter(
        Medicion.momento == momento, 
        Medicion.anio == anio,
        Medicion.sede_id == sede_coordinador_actual
    ).first()
    
    if carga_existente:
        raise HTTPException(
            status_code=409, 
            detail=f"Tu sede ya tiene registros cargados para el Momento {momento} del año {anio}. Por favor, elimínelos desde el Historial antes de volver a cargarlos."
        )"""

content = re.sub(
    r'# REGLA DE NEGOCIO: Evitar duplicidad de cargas\s+carga_existente = db\.query\(Medicion\)\.filter\(Medicion\.momento == momento, Medicion\.anio == anio\)\.first\(\)\s+if carga_existente:\s+raise HTTPException\(\s*status_code=409,\s*detail=f"Ya existen.*?volver a cargarlo\."\s*\)',
    new_rule,
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Regla de negocio de duplicidad parcheada para que dependa de la sede.")
