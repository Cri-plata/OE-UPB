import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.models import Medicion
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

medicion = session.query(Medicion).first()
if medicion and medicion.respuestas:
    keys = list(medicion.respuestas.keys())
    print("TOTAL COLUMNAS:", len(keys))
    print("ALGUNAS COLUMNAS (Muestra de 30):")
    for k in keys[:30]:
        print("-", k)
    
    print("\nVALORES DE EJEMPLO PARA COLUMNAS QUE SUENEN A SALARIO, TRABAJO O SATISFACCION:")
    for k, v in medicion.respuestas.items():
        k_lower = k.lower()
        if 'salario' in k_lower or 'trabaj' in k_lower or 'emple' in k_lower or 'ingreso' in k_lower or 'satisfac' in k_lower or 'actualmente' in k_lower:
            print(f"{k}: {v}")
else:
    print("No hay mediciones en la BD.")
