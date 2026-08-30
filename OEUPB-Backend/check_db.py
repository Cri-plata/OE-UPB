from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.models import Egresado, Medicion

engine = create_engine("mysql+pymysql://root:@localhost/oeupb")
Session = sessionmaker(bind=engine)
session = Session()

total = session.query(Egresado).count()
print(f"Total Egresados: {total}")

medicion = session.query(Medicion).first()
if medicion:
    print(f"Llaves en la primera medición: {list(medicion.respuestas.keys())}")
else:
    print("No hay mediciones.")
