import sys
import os

# Asegurar que Python reconozca los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.database import Base, engine
from domain.models import Usuario

def init_db():
    print("Creando tablas en MySQL...")
    try:
        Base.metadata.create_all(bind=engine)
        print("¡Tablas creadas exitosamente!")
    except Exception as e:
        print(f"Error al conectar con MySQL: {e}")

if __name__ == "__main__":
    init_db()
