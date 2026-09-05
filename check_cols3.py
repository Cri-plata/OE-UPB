import pandas as pd
df0 = pd.read_excel(r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0_Test.xlsx", nrows=0)
print(list(df0.columns)[:30])
