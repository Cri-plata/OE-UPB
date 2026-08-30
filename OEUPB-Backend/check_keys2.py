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
    for k, v in medicion.respuestas.items():
        if 'actualmente usted' in k.lower() or 'actividad remunerada' in k.lower():
            print(f"{k}: {v}")
