import pandas as pd

file_path = r"C:\Users\USUARIO\Documents\U sexto\egresados\Consolidado Momento 1 2025.xlsx"

try:
    df = pd.read_excel(file_path)
    print("TOTAL COLUMNAS:", len(df.columns))
    for col in df.columns:
        print(f"- {col}")
except Exception as e:
    print(f"Error leyendo el archivo: {e}")
