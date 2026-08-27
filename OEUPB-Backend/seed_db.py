import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from infrastructure.database import SessionLocal
from domain.models import Usuario
from application.auth_service import get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
        # Verificar si ya existe
        admin = db.query(Usuario).filter(Usuario.correo == "admin@upb.edu.co").first()
        if not admin:
            nuevo_admin = Usuario(
                nombre="Administrador CTIC",
                correo="admin@upb.edu.co",
                contrasena_hash=get_password_hash("admin123"),
                rol="Admin_CTIC",
                sede_id=None
            )
            db.add(nuevo_admin)
            db.commit()
            print("Usuario administrador creado: admin@upb.edu.co / admin123")
        else:
            print("El usuario administrador ya existe.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
