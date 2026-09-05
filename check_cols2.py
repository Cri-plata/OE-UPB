import pandas as pd
df0 = pd.read_excel(r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0_Test.xlsx", nrows=0)
cols = list(df0.columns)
print("Todas las cols:", cols)
