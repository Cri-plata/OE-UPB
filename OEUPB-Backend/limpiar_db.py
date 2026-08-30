import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.models import Egresado, Medicion
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

try:
    session.query(Medicion).delete()
    session.query(Egresado).delete()
    session.commit()
    print("¡Limpieza profunda completada! Todos los egresados y mediciones han sido eliminados de MySQL.")
except Exception as e:
    print(f"Error: {e}")
