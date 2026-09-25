import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from infrastructure.database import SessionLocal
from domain.models import Usuario
from application.auth_service import expiracion_credencial_inicial, generar_contrasena_temporal, get_password_hash

def seed_admin():
    db = SessionLocal()
    try:
        # Verificar si ya existe
        admin = db.query(Usuario).filter(Usuario.correo == "admin@upb.edu.co").first()
        if not admin:
            contrasena_temporal = generar_contrasena_temporal()
            nuevo_admin = Usuario(
                nombre="Administrador CTIC",
                correo="admin@upb.edu.co",
                contrasena_hash=get_password_hash(contrasena_temporal),
                rol="Admin_CTIC",
                sede_id=None,
                debe_cambiar_contrasena=True,
                credencial_temporal_expira_en=expiracion_credencial_inicial(),
            )
            db.add(nuevo_admin)
            db.commit()
            print(
                "Usuario administrador creado: admin@upb.edu.co / "
                f"{contrasena_temporal}"
            )
            print("Guarde esta contraseña temporal: no volverá a mostrarse.")
        else:
            print("El usuario administrador ya existe.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
