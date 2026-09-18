path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\reportes_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

import re

# Fix get_reporte_general
new_code_general = """    total_query = db.query(Egresado)
    programas_query = db.query(Egresado.programa)
    query_med = db.query(Medicion)
    
    if current_user.get('rol') == 'Coordinador_Sede':
        sede_id = current_user.get('sede_id')
        # Filtrar egresados (tienen sede? Si no, los cruzamos con mediciones)
        # Por ahora, filtramos las mediciones por la sede
        query_med = query_med.filter(Medicion.sede_id == sede_id)
        
        # Para el total de egresados de esta sede, usamos los que tienen mediciones en esta sede
        # Para simplificar y evitar joins complejos si egresados no tiene sede_id, filtramos as
        from sqlalchemy import text
        # ...
        
    total = total_query.count()
    programas = programas_query.all()"""

# I'll just simply define query_med so it doesn't crash, and actually apply the filter
content = re.sub(
    r'total = db\.query\(Egresado\)\.count\(\)\s*programas = db\.query\(Egresado\.programa\)\.all\(\)',
    """
    query_med = db.query(Medicion)
    query_egresados = db.query(Egresado)
    
    if current_user.get('rol') == 'Coordinador_Sede':
        query_med = query_med.filter(Medicion.sede_id == current_user.get('sede_id'))
        query_egresados = query_egresados.filter(Egresado.numero_documento.in_(db.query(Medicion.egresado_documento).filter(Medicion.sede_id == current_user.get('sede_id'))))

    total = query_egresados.count()
    programas = query_egresados.with_entities(Egresado.programa).all()
""",
    content
)

# And fix get_tendencias as well if it's not filtered
content = re.sub(
    r'mediciones = db\.query\(Medicion, Egresado\.programa\)\.join\(Egresado, Medicion\.egresado_documento == Egresado\.numero_documento\)\.all\(\)',
    """
    query = db.query(Medicion, Egresado.programa).join(Egresado, Medicion.egresado_documento == Egresado.numero_documento)
    if current_user.get('rol') == 'Coordinador_Sede':
        query = query.filter(Medicion.sede_id == current_user.get('sede_id'))
    mediciones = query.all()
""",
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("reportes_router.py parcheado para arreglar query_med undefined y añadir filtrado.")
