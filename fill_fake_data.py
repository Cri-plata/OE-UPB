import pandas as pd
import random

nombres = ["Juan", "Maria", "Carlos", "Ana", "Luis", "Laura", "Andres", "Marta", "Diego", "Sofia", "Jorge", "Valentina", "David", "Camila", "Daniel", "Daniela", "Alejandro", "Isabella", "Sebastian", "Valeria", "Mateo", "Mariana", "Samuel", "Gabriela", "Julian"]
apellidos = ["Gomez", "Rodriguez", "Lopez", "Perez", "Gonzalez", "Martinez", "Garcia", "Ramirez", "Torres", "Ruiz", "Sanchez", "Diaz", "Vasquez", "Cruz", "Reyes", "Morales", "Ortiz", "Gutierrez", "Navarro", "Ramos", "Castro", "Jimenez", "Rojas", "Silva", "Mendoza"]

def gen_fake_person():
    return {
        "NUMERO_DOCUMENTO": str(random.randint(1000000000, 1999999999)),
        "PRIMER NOMBRE": random.choice(nombres).upper(),
        "SEGUNDO_NOMBRE": random.choice(nombres).upper(),
        "PRIMER_APELLIDO": random.choice(apellidos).upper(),
        "SEGUNDO APELLIDO": random.choice(apellidos).upper(),
        "TIPO DOCUMENTO": "CC"
    }

file0 = r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0.xlsx"
file1 = r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 1.xlsx"

out_file0 = r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0_Test.xlsx"
out_file1 = r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 1_Test.xlsx"

print("Cargando Momento 0...")
df0 = pd.read_excel(file0)
print("Cargando Momento 1...")
df1 = pd.read_excel(file1)

for col in ["NUMERO_DOCUMENTO", "PRIMER NOMBRE", "SEGUNDO_NOMBRE", "PRIMER_APELLIDO", "SEGUNDO APELLIDO", "TIPO DOCUMENTO"]:
    if col in df0.columns:
        df0[col] = df0[col].astype("object")
    if col in df1.columns:
        df1[col] = df1[col].astype("object")

personas_por_programa = {}

print("Rellenando Momento 0...")
for idx, row in df0.iterrows():
    prog = str(row.get("PROGRAMA", "DESCONOCIDO")).strip().upper()
    
    p = gen_fake_person()
    
    if prog not in personas_por_programa:
        personas_por_programa[prog] = []
    
    personas_por_programa[prog].append(p)
    
    for k, v in p.items():
        if k in df0.columns:
            df0.at[idx, k] = v

print("Rellenando Momento 1...")
for idx, row in df1.iterrows():
    prog = str(row.get("PROGRAMA", "DESCONOCIDO")).strip().upper()
    
    matched_key = None
    if prog in personas_por_programa and len(personas_por_programa[prog]) > 0:
        matched_key = prog
    else:
        for k in personas_por_programa.keys():
            if k[:10] == prog[:10] and len(personas_por_programa[k]) > 0:
                matched_key = k
                break
                
    if matched_key:
        p = personas_por_programa[matched_key].pop(0)
        for k, v in p.items():
            if k in df1.columns:
                df1.at[idx, k] = v
    else:
        p = gen_fake_person()
        for k, v in p.items():
            if k in df1.columns:
                df1.at[idx, k] = v

print("Guardando archivos nuevos...")
df0.to_excel(out_file0, index=False)
df1.to_excel(out_file1, index=False)
print("¡Archivos rellenados con éxito!")
