with open(r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

out_lines = []
skip = False
for line in lines:
    if "df = df.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])" in line:
        out_lines.append("""
    # 2. Separar anonimos de identificados para no borrar anonimos por error
    df_con_cedula = df.dropna(subset=['NUMERO_DOCUMENTO'])
    df_anonimos = df[df['NUMERO_DOCUMENTO'].isna()]

    # 3. Ordenar y eliminar duplicados SOLO en los que tienen cedula
    df_con_cedula = df_con_cedula.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])
    df_con_cedula = df_con_cedula.drop_duplicates(subset=['NUMERO_DOCUMENTO'], keep='last')
    
    # 4. Volver a unir
    import pandas as pd
    df = pd.concat([df_con_cedula, df_anonimos], ignore_index=True)
""")
        skip = True
        continue
        
    if skip:
        if "total_final = len(df)" in line:
            skip = False
            out_lines.append(line)
    else:
        out_lines.append(line)

with open(r"C:\Users\USUARIO\Documents\U\OE UPB\OEUPB-Backend\presentation\carga_router.py", "w", encoding="utf-8") as f:
    f.writelines(out_lines)
