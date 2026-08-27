import pandas as pd
import warnings
warnings.filterwarnings('ignore')

file_path = r"C:\Users\USUARIO\Documents\U sexto\egresados\Consolidado Momento 1 2025.xlsx"

try:
    print("Leyendo Excel...")
    df = pd.read_excel(file_path)
    
    print("Eliminando espacios en columnas...")
    df.columns = df.columns.str.strip()
    
    print("Verificando nulos...")
    # Simulando la lógica
    for index, row in df.iterrows():
        pass # esto toma un par de milisegundos
        
    print("Convirtiendo fecha...")
    df['FECHA_GRADO'] = pd.to_datetime(df['FECHA_GRADO'], errors='coerce')
    
    print("Ordenando...")
    df = df.sort_values(by=['NUMERO_DOCUMENTO', 'FECHA_GRADO'])
    
    print("Borrando duplicados...")
    df = df.drop_duplicates(subset=['NUMERO_DOCUMENTO'], keep='last')
    
    print("Éxito. Quedaron", len(df), "filas.")
except Exception as e:
    import traceback
    traceback.print_exc()
