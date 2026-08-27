import pandas as pd
import sys

file_path = r"C:\Users\USUARIO\Documents\U sexto\egresados\Consolidado Momento 1 2025.xlsx"

try:
    df = pd.read_excel(file_path)
    print("Columnas encontradas en el archivo:")
    print(df.columns.tolist())
    print("\nPrimeras 3 filas:")
    print(df.head(3).to_string())
except Exception as e:
    print(f"Error leyendo el archivo: {e}")
