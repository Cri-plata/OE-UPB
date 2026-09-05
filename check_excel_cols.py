import pandas as pd
import os

df0 = pd.read_excel(r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0.xlsx", nrows=0)
print("Momento 0 cols:", list(df0.columns)[:15])

df1 = pd.read_excel(r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 1.xlsx", nrows=0)
print("Momento 1 cols:", list(df1.columns)[:15])
