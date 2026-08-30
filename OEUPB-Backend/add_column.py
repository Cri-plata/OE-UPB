from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE mediciones ADD COLUMN anio INT;"))
        conn.commit()
        print("Columna 'anio' agregada a la tabla 'mediciones'.")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("La columna 'anio' ya existía.")
    else:
        print("Error agregando columna:", e)
