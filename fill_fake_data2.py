import pandas as pd
import random
import datetime

nombres_m = ["JUAN", "CARLOS", "LUIS", "ANDRES", "DIEGO", "JORGE", "DAVID", "DANIEL", "ALEJANDRO", "SEBASTIAN", "MATEO", "SAMUEL", "JULIAN"]
nombres_f = ["MARIA", "ANA", "LAURA", "MARTA", "SOFIA", "VALENTINA", "CAMILA", "DANIELA", "ISABELLA", "VALERIA", "MARIANA", "GABRIELA"]
apellidos = ["GOMEZ", "RODRIGUEZ", "LOPEZ", "PEREZ", "GONZALEZ", "MARTINEZ", "GARCIA", "RAMIREZ", "TORRES", "RUIZ", "SANCHEZ", "DIAZ", "VASQUEZ", "CRUZ", "REYES", "MORALES", "ORTIZ", "GUTIERREZ", "NAVARRO", "RAMOS", "CASTRO", "JIMENEZ", "ROJAS", "SILVA", "MENDOZA"]

def gen_fake_person():
    is_m = random.choice([True, False])
    nombres = nombres_m if is_m else nombres_f
    sexo = "Hombre" if is_m else "Mujer"
    
    primer_nombre = random.choice(nombres)
    segundo_nombre = random.choice(nombres)
    primer_apellido = random.choice(apellidos)
    segundo_apellido = random.choice(apellidos)
    
    # Fecha nacimiento random entre 1995 y 2001
    start_date = datetime.date(1995, 1, 1)
    end_date = datetime.date(2001, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    
    email = f"{primer_nombre.lower()}.{primer_apellido.lower()}@example.com"
    celular = f"3{random.randint(100000000, 299999999)}"
    
    return {
        "NUMERO_DOCUMENTO": str(random.randint(1000000000, 1999999999)),
        "PRIMER NOMBRE": primer_nombre,
        "SEGUNDO_NOMBRE": segundo_nombre,
        "PRIMER_APELLIDO": primer_apellido,
        "SEGUNDO APELLIDO": segundo_apellido,
        "TIPO DOCUMENTO": "CC",
        "SEXO BIOLGICO": sexo,
        "FECHA NACIMIENTO": random_date.strftime("%Y-%m-%d"),
        "PAIS": "Colombia",
        "EMAIL": email,
        "EMAIL OPCIONAL": email,
        "TELEFONO": str(random.randint(2000000, 9999999)),
        "CELULAR": celular,
        "CODIGO_IES": "1214",
        "IES": "UNIVERSIDAD PONTIFICIA BOLIVARIANA"
    }

file0 = r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 0_Test.xlsx"
file1 = r"C:\Users\USUARIO\Documents\U sexto\otros\Momento 1_Test.xlsx"

print("Cargando Momento 0...")
df0 = pd.read_excel(file0)
print("Cargando Momento 1...")
df1 = pd.read_excel(file1)

# El script lee de las columnas, necesitamos saber la key exacta para "SEXO BIOLOGICO"
# ya que en pandas puede venir mal parseada.
cols0 = list(df0.columns)
sexo_col0 = next((c for c in cols0 if "SEXO" in c), "SEXO BIOLÓGICO")
cols1 = list(df1.columns)
sexo_col1 = next((c for c in cols1 if "SEXO" in c), "SEXO BIOLÓGICO")

# Castear a object
for df in [df0, df1]:
    for col in df.columns:
        if df[col].dtype == 'float64' and df[col].isna().all():
            df[col] = df[col].astype("object")

personas_por_programa = {}

print("Rellenando Momento 0...")
for idx, row in df0.iterrows():
    prog = str(row.get("PROGRAMA", "DESCONOCIDO")).strip().upper()
    p = gen_fake_person()
    
    # Arreglar la llave de sexo dependiendo del DF
    p[sexo_col0] = p.pop("SEXO BIOLGICO")
    
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
    else:
        p = gen_fake_person()
        
    p[sexo_col1] = p.pop(sexo_col0, p.get("SEXO BIOLGICO"))
        
    for k, v in p.items():
        if k in df1.columns:
            df1.at[idx, k] = v

print("Guardando archivos nuevos...")
df0.to_excel(file0, index=False)
df1.to_excel(file1, index=False)
print("¡Archivos rellenados con éxito!")
