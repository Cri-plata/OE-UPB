import re

path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

find_logic = """    # 2. Ordenar por Cdula y luego por Fecha de Grado (de la ms antigua a la ms reciente)
    df = df.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])
    
    # 3. Eliminar duplicados manteniendo solo la LTIMA fila (la fecha ms reciente)
    df = df.drop_duplicates(subset=['NUMERO_DOCUMENTO'], keep='last')"""

# If the exact text isn't found due to encoding, let's use regex
content = re.sub(
    r'df = df\.sort_values\(by=\[\'NUMERO_DOCUMENTO\', \'FECHA_GRADO\'\]\)\s*df = df\.drop_duplicates\(subset=\[\'NUMERO_DOCUMENTO\'\], keep=\'last\'\)',
    """
    # 2. Separar annimos de identificados para no borrar annimos por error (NaN == NaN)
    df_con_cedula = df.dropna(subset=['NUMERO_DOCUMENTO'])
    df_anonimos = df[df['NUMERO_DOCUMENTO'].isna()]

    # 3. Ordenar y eliminar duplicados SOLO en los que tienen cdula
    df_con_cedula = df_con_cedula.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])
    df_con_cedula = df_con_cedula.drop_duplicates(subset=['NUMERO_DOCUMENTO'], keep='last')
    
    # 4. Volver a unir
    import pandas as pd
    df = pd.concat([df_con_cedula, df_anonimos], ignore_index=True)""",
    content
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Lógica de doble titulación reparada para ignorar a los anónimos.")
