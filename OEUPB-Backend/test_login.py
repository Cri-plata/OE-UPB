import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from infrastructure.database import SessionLocal
from domain.models import Usuario
from application.auth_service import verify_password

def test_login():
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.correo == "admin@upb.edu.co").first()
    if not user:
        print("USUARIO NO ENCONTRADO EN LA BD")
        return
    
    print(f"Usuario encontrado: {user.correo}")
    print(f"Hash en BD: {user.contrasena_hash}")
    
    match = verify_password("admin123", user.contrasena_hash)
    print(f"¿La contraseña 'admin123' coincide?: {match}")
    
    db.close()

if __name__ == "__main__":
    test_login()
