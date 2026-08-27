import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from infrastructure.database import SessionLocal
from domain.models import Usuario

def check_db():
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    for u in usuarios:
        print(f"ID: {u.id} - Nombre: {u.nombre} - Correo: {u.correo} - Rol: {u.rol}")
    db.close()

if __name__ == "__main__":
    check_db()
