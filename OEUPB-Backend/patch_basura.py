import re

path = r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

find_text = "df.columns = df.columns.str.strip()"
replace_text = """df.columns = df.columns.str.strip()

    # REGLA DE LIMPIEZA: Eliminar filas basura del final del Excel
    # Reemplazar celdas con solo espacios por NaN
    import numpy as np
    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    
    # Si la fila no tiene ni Cdula ni Programa, es casi seguro una fila de totales o basura
    df.dropna(subset=['NUMERO_DOCUMENTO', 'PROGRAMA'], how='all', inplace=True)
"""

content = content.replace(find_text, replace_text)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Limpieza de filas basura añadida.")
