import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from domain.models import AuditoriaCuenta, Base, Carga, Egresado, Medicion, Sede, Usuario
from infrastructure.database import get_db
from main import app


class RbacPermisosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()
        db.add_all([
            Sede(id=1, codigo="BUC", nombre="Bucaramanga"),
            Sede(id=2, codigo="MED", nombre="Medellín"),
        ])
        usuarios = [
            Usuario(nombre="CTIC", correo="ctic@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Admin_CTIC", sede_id=None),
            Usuario(nombre="Coord 1", correo="coord1@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=1),
            Usuario(nombre="Coord 2", correo="coord2@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=2),
            Usuario(nombre="Consulta 1", correo="consulta1@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Usuario_Consulta", sede_id=1, etiqueta="Profesor", permisos=["ver_publicaciones"], programas=["Derecho"]),
            Usuario(nombre="Consulta 2", correo="consulta2@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Usuario_Consulta", sede_id=2, etiqueta="Rector", permisos=[], programas=["Medicina"]),
        ]
        db.add_all(usuarios)
        db.add_all([
            Egresado(numero_documento="123", primer_nombre="Ana", primer_apellido="Uno", programa="Derecho"),
            Egresado(numero_documento="456", primer_nombre="Beto", primer_apellido="Dos", programa="Medicina"),
        ])
        db.flush()
        actor = next(u for u in usuarios if u.correo == "ctic@upb.edu.co")
        carga1 = Carga(nombre_archivo="s1.xlsx", hash_archivo="a" * 64, usuario_id=actor.id, sede_id=1, momento=0, anio_grado=2025, estado="vigente", version=1, registros=1)
        carga2 = Carga(nombre_archivo="s2.xlsx", hash_archivo="b" * 64, usuario_id=actor.id, sede_id=2, momento=1, anio_grado=2024, estado="vigente", version=1, registros=2)
        db.add_all([carga1, carga2])
        db.flush()
        db.add_all([
            Medicion(carga_id=carga1.id, egresado_documento="123", momento=0, anio=2025, sede_id=1, respuestas={}),
            Medicion(carga_id=carga2.id, egresado_documento="123", momento=5, anio=2020, sede_id=2, respuestas={}),
            Medicion(carga_id=carga2.id, egresado_documento="456", momento=1, anio=2024, sede_id=2, respuestas={}),
        ])
        db.commit(); db.close()

        def override_db():
            session = self.Session()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def login(self, correo: str) -> dict:
        respuesta = self.client.post("/api/auth/login", json={"correoInstitucional": correo, "contrasena": "ClaveSegura2026"})
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        return {"Authorization": f"Bearer {respuesta.json()['token']}"}

    def test_matriz_deniega_escalada_y_datos_privados(self):
        admin = self.login("ctic@upb.edu.co")
        coordinador = self.login("coord1@upb.edu.co")
        consulta = self.login("consulta1@upb.edu.co")

        self.assertEqual(self.client.get("/api/reportes/general", headers=admin).status_code, 403)
        self.assertEqual(self.client.get("/api/reportes/general", headers=consulta).status_code, 403)
        self.assertEqual(self.client.get("/api/directorio/tabla", headers=consulta).status_code, 403)
        self.assertEqual(self.client.get("/api/carga/historial", headers=consulta).status_code, 403)
        self.assertEqual(self.client.get("/api/usuarios/", headers=consulta).status_code, 403)
        reporte = self.client.get("/api/reportes/general", headers=coordinador)
        self.assertEqual(reporte.status_code, 200, reporte.text)
        self.assertEqual(reporte.json()["total_egresados"], 1)

        escalada_admin = self.client.post("/api/usuarios/", headers=admin, json={
            "nombre": "Consulta", "correo": "otra@upb.edu.co", "rol": "Usuario_Consulta",
            "sede_id": 1, "numero_documento": "10000001", "etiqueta": "Profesor", "permisos": [], "programas": [],
        })
        escalada_coord = self.client.post("/api/usuarios/", headers=coordinador, json={
            "nombre": "Coordinador", "correo": "otro@upb.edu.co", "rol": "Coordinador_Sede", "sede_id": 1, "numero_documento": "10000002",
        })
        self.assertEqual(escalada_admin.status_code, 403)
        self.assertEqual(escalada_coord.status_code, 403)

    def test_programas_y_usuarios_se_aislan_por_sede(self):
        coordinador = self.login("coord1@upb.edu.co")
        programas = self.client.get("/api/usuarios/programas-asignables", headers=coordinador)
        self.assertEqual(programas.status_code, 200, programas.text)
        self.assertEqual(programas.json(), ["Derecho"])

        usuarios = self.client.get("/api/usuarios/", headers=coordinador)
        self.assertEqual([u["correo"] for u in usuarios.json()], ["consulta1@upb.edu.co"])

        invalido = self.client.post("/api/usuarios/", headers=coordinador, json={
            "nombre": "Fuera", "correo": "fuera@upb.edu.co", "rol": "Usuario_Consulta", "numero_documento": "10000003",
            "sede_id": 1, "etiqueta": "Profesor",
            "permisos": ["ver_publicaciones"], "programas": ["Medicina"],
        })
        self.assertEqual(invalido.status_code, 422)

    def test_directorio_no_filtra_historial_de_otra_sede(self):
        coordinador = self.login("coord1@upb.edu.co")
        respuesta = self.client.get("/api/directorio/tabla", headers=coordinador)
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        self.assertEqual(respuesta.json()["total"], 1)
        self.assertEqual(respuesta.json()["data"][0]["encuestas"], "M0 (2025)")

    def test_desactivacion_revoca_token_y_borrado_es_auditado(self):
        admin = self.login("ctic@upb.edu.co")
        token_coordinador = self.login("coord1@upb.edu.co")
        db = self.Session()
        objetivo_id = db.query(Usuario).filter(Usuario.correo == "coord1@upb.edu.co").one().id
        db.close()

        desactivar = self.client.post(f"/api/usuarios/{objetivo_id}/desactivar", headers=admin)
        self.assertEqual(desactivar.status_code, 200, desactivar.text)
        self.assertFalse(desactivar.json()["activo"])
        self.assertEqual(self.client.get("/api/reportes/general", headers=token_coordinador).status_code, 401)
        login_bloqueado = self.client.post("/api/auth/login", json={"correoInstitucional": "coord1@upb.edu.co", "contrasena": "ClaveSegura2026"})
        self.assertEqual(login_bloqueado.status_code, 401)

        borrar = self.client.request(
            "DELETE", f"/api/usuarios/{objetivo_id}/permanente", headers=admin,
            json={"motivo": "Cuenta duplicada confirmada por soporte"},
        )
        self.assertEqual(borrar.status_code, 200, borrar.text)
        db = self.Session()
        self.assertIsNone(db.query(Usuario).filter(Usuario.id == objetivo_id).first())
        self.assertEqual(db.query(AuditoriaCuenta).filter(AuditoriaCuenta.objetivo_id == objetivo_id).count(), 1)
        db.close()

    def test_coordinador_no_administra_consulta_de_otra_sede(self):
        coordinador = self.login("coord1@upb.edu.co")
        db = self.Session()
        objetivo_id = db.query(Usuario).filter(Usuario.correo == "consulta2@upb.edu.co").one().id
        db.close()
        respuesta = self.client.post(f"/api/usuarios/{objetivo_id}/desactivar", headers=coordinador)
        self.assertEqual(respuesta.status_code, 403)
        reemision = self.client.post(
            f"/api/usuarios/{objetivo_id}/regenerar-credencial-temporal",
            headers=coordinador,
            json={"motivo": "Solicitud de recuperación reportada por soporte"},
        )
        self.assertEqual(reemision.status_code, 403)

    def test_reduccion_de_permisos_revoca_token_anterior(self):
        coordinador = self.login("coord1@upb.edu.co")
        token_consulta = self.login("consulta1@upb.edu.co")
        db = self.Session()
        objetivo_id = db.query(Usuario).filter(Usuario.correo == "consulta1@upb.edu.co").one().id
        db.close()

        cambio = self.client.patch(
            f"/api/usuarios/{objetivo_id}",
            headers=coordinador,
            json={
                "etiqueta": "Profesor",
                "permisos": [],
                "programas": ["Derecho"],
            },
        )
        self.assertEqual(cambio.status_code, 200, cambio.text)
        self.assertEqual(cambio.json()["version_autorizacion"], 2)
        self.assertEqual(self.client.get("/api/usuarios/", headers=token_consulta).status_code, 401)


if __name__ == "__main__":
    unittest.main()
