import re

path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the strict validation block
content = re.sub(r'# Validar fila por fila.*?if errores:\s*return CargaResponse.*?errores=errores\)', '', content, flags=re.DOTALL)

# 2. Modify the DB insertion loop
find_loop = """    for index, row in df.iterrows():
        doc = str(row.get('NUMERO_DOCUMENTO'))
        
        # 1. Crear o Actualizar al Egresado
        egresado = db.query(Egresado).filter(Egresado.numero_documento == doc).first()
        if not egresado:
            egresado = Egresado(
                numero_documento=doc,
                primer_nombre=str(row.get('PRIMER NOMBRE', '')),
                primer_apellido=str(row.get('PRIMER_APELLIDO', '')),
                programa=str(row.get('PROGRAMA', '')),
                fecha_grado=row.get('FECHA_GRADO') if pd.notnull(row.get('FECHA_GRADO')) else None
            )
            db.add(egresado)
        else:
            # Actualizamos fecha de grado si es ms reciente
            if row.get('FECHA_GRADO') and pd.notnull(row.get('FECHA_GRADO')):
                if not egresado.fecha_grado or row.get('FECHA_GRADO') > egresado.fecha_grado:
                    egresado.fecha_grado = row.get('FECHA_GRADO')
                    egresado.programa = str(row.get('PROGRAMA', ''))

        db.commit() # Aseguramos que el egresado exista para la llave fornea
"""

replace_loop = """    for index, row in df.iterrows():
        # Manejo de Cdulas vacas (Annimos)
        is_empty_doc = pd.isna(row.get('NUMERO_DOCUMENTO')) or str(row.get('NUMERO_DOCUMENTO')).strip() == ''
        
        doc = None
        if not is_empty_doc:
            doc = str(row.get('NUMERO_DOCUMENTO'))
            if doc.endswith('.0'):
                doc = doc[:-2]
                
        # 1. Crear o Actualizar al Egresado SOLO si hay cdula
        if doc:
            egresado = db.query(Egresado).filter(Egresado.numero_documento == doc).first()
            if not egresado:
                
                # Manejo de Nombres vacos o sin segundo nombre
                p_nombre = str(row.get('PRIMER NOMBRE', '')) if not pd.isna(row.get('PRIMER NOMBRE')) else "Sin Nombre"
                p_apellido = str(row.get('PRIMER_APELLIDO', '')) if not pd.isna(row.get('PRIMER_APELLIDO')) else ""
                prog = str(row.get('PROGRAMA', '')) if not pd.isna(row.get('PROGRAMA')) else "Sin Programa"
                
                egresado = Egresado(
                    numero_documento=doc,
                    primer_nombre=p_nombre,
                    primer_apellido=p_apellido,
                    programa=prog,
                    fecha_grado=row.get('FECHA_GRADO') if pd.notnull(row.get('FECHA_GRADO')) else None
                )
                db.add(egresado)
            else:
                # Actualizamos fecha de grado si es mas reciente
                if row.get('FECHA_GRADO') and pd.notnull(row.get('FECHA_GRADO')):
                    if not egresado.fecha_grado or row.get('FECHA_GRADO') > egresado.fecha_grado:
                        egresado.fecha_grado = row.get('FECHA_GRADO')
                        
            db.commit() # Aseguramos que el egresado exista para la llave foranea
"""
# We use regex to replace the loop carefully, as there might be slight encoding differences in the comments
content = re.sub(r'    for index, row in df\.iterrows\(\):.*?db\.commit\(\) # Aseguramos que el egresado exista para la llave for.*?a', replace_loop, content, flags=re.DOTALL)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Backend modificado para soportar encuestas anónimas y nombres vacíos.")
