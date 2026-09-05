import pandas as pd

df0 = pd.read_excel(r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0.xlsx")
print("Momento 0 length:", len(df0))
print(df0[['NUMERO_DOCUMENTO', 'PRIMER NOMBRE', 'ID RESPUESTA', 'PROGRAMA']].head())

df1 = pd.read_excel(r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 1.xlsx")
print("Momento 1 length:", len(df1))
print(df1[['NUMERO_DOCUMENTO', 'PRIMER NOMBRE', 'ID RESPUESTA', 'PROGRAMA']].head())
