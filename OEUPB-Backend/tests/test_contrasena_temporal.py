import unittest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import (
    generar_contrasena_temporal,
    get_current_user,
    get_password_hash,
    verify_password,
    validate_security_settings,
)
from domain.models import AuditoriaCuenta, Base, Sede, Usuario
from infrastructure.database import get_db
from main import app


class ContrasenaTemporalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.temporal = generar_contrasena_temporal()

        db = self.Session()
        db.add(Sede(id=1, codigo="BUC", nombre="Bucaramanga"))
        db.add(
            Usuario(
                nombre="Usuario temporal",
                correo="temporal@upb.edu.co",
                contrasena_hash=get_password_hash(self.temporal),
                rol="Coordinador_Sede",
                sede_id=1,
                debe_cambiar_contrasena=True,
            )
        )
        db.add(
            Usuario(
                nombre="Administrador",
                correo="admin@upb.edu.co",
                contrasena_hash=get_password_hash("AdminSegura2026"),
                rol="Admin_CTIC",
                sede_id=None,
                debe_cambiar_contrasena=False,
            )
        )
        db.commit()
        db.close()

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

    def test_temporal_es_aleatoria_y_compleja(self):
        self.assertGreaterEqual(len(self.temporal), 14)
        self.assertTrue(any(c.isupper() for c in self.temporal))
        self.assertTrue(any(c.islower() for c in self.temporal))
        self.assertTrue(any(c.isdigit() for c in self.temporal))

    def test_primer_ingreso_obliga_cambio_y_revoca_temporal(self):
        login = self.client.post(
            "/api/auth/login",
            json={
                "correoInstitucional": "temporal@upb.edu.co",
                "contrasena": self.temporal,
            },
        )
        self.assertEqual(login.status_code, 200, login.text)
        self.assertTrue(login.json()["usuario"]["debeCambiarContrasena"])
        token = login.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        bloqueada = self.client.get("/api/carga/historial", headers=headers)
        self.assertEqual(bloqueada.status_code, 403, bloqueada.text)
        self.assertEqual(
            bloqueada.json()["detail"]["codigo"],
            "CAMBIO_CONTRASENA_REQUERIDO",
        )

        cambio = self.client.post(
            "/api/auth/cambiar-contrasena-temporal",
            headers=headers,
            json={
                "nuevaContrasena": "NuevaClave2026",
                "confirmarContrasena": "NuevaClave2026",
            },
        )
        self.assertEqual(cambio.status_code, 200, cambio.text)
        self.assertFalse(cambio.json()["usuario"]["debeCambiarContrasena"])

        login_anterior = self.client.post(
            "/api/auth/login",
            json={
                "correoInstitucional": "temporal@upb.edu.co",
                "contrasena": self.temporal,
            },
        )
        self.assertEqual(login_anterior.status_code, 401)

        login_nuevo = self.client.post(
            "/api/auth/login",
            json={
                "correoInstitucional": "temporal@upb.edu.co",
                "contrasena": "NuevaClave2026",
            },
        )
        self.assertEqual(login_nuevo.status_code, 200, login_nuevo.text)

    def test_creacion_devuelve_temporal_una_sola_vez(self):
        app.dependency_overrides[get_current_user] = lambda: {
            "correo": "admin@upb.edu.co",
            "rol": "Admin_CTIC",
            "sede_id": None,
            "debe_cambiar_contrasena": False,
        }
        creacion = self.client.post(
            "/api/usuarios/",
            json={
                "nombre": "Nuevo coordinador",
                "correo": "nuevo@upb.edu.co",
                "rol": "Coordinador_Sede",
                "sede_id": 1,
                "numero_documento": "1098765432",
            },
        )
        self.assertEqual(creacion.status_code, 200, creacion.text)
        temporal = creacion.json()["contrasena_temporal"]
        self.assertEqual(temporal, "1098765432")

        db = self.Session()
        creado = db.query(Usuario).filter(Usuario.correo == "nuevo@upb.edu.co").one()
        self.assertTrue(creado.debe_cambiar_contrasena)
        self.assertNotEqual(creado.contrasena_hash, temporal)
        self.assertTrue(verify_password(temporal, creado.contrasena_hash))
        db.close()

        listado = self.client.get("/api/usuarios/")
        self.assertEqual(listado.status_code, 200, listado.text)
        nuevo = next(u for u in listado.json() if u["correo"] == "nuevo@upb.edu.co")
        self.assertNotIn("contrasena_temporal", nuevo)

    def test_temporal_vencida_se_rechaza_y_reemision_revoca_la_anterior(self):
        db = self.Session()
        usuario = db.query(Usuario).filter(Usuario.correo == "temporal@upb.edu.co").one()
        anterior = self.temporal
        usuario.credencial_temporal_expira_en = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        objetivo_id = usuario.id
        db.commit(); db.close()

        vencida = self.client.post("/api/auth/login", json={"correoInstitucional": "temporal@upb.edu.co", "contrasena": anterior})
        self.assertEqual(vencida.status_code, 401)
        self.assertEqual(vencida.json()["detail"]["codigo"], "CREDENCIAL_TEMPORAL_VENCIDA")

        app.dependency_overrides[get_current_user] = lambda: {
            "usuario_id": 2, "correo": "admin@upb.edu.co", "rol": "Admin_CTIC",
            "sede_id": None, "debe_cambiar_contrasena": False,
        }
        reemision = self.client.post(
            f"/api/usuarios/{objetivo_id}/regenerar-credencial-temporal",
            json={"motivo": "El usuario perdió su credencial antes del ingreso"},
        )
        self.assertEqual(reemision.status_code, 200, reemision.text)
        nueva = reemision.json()["contrasena_temporal"]
        self.assertNotEqual(nueva, anterior)
        self.assertEqual(self.client.post("/api/auth/login", json={"correoInstitucional": "temporal@upb.edu.co", "contrasena": anterior}).status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login", json={"correoInstitucional": "temporal@upb.edu.co", "contrasena": nueva}).status_code, 200)
        db = self.Session()
        self.assertEqual(db.query(AuditoriaCuenta).filter(AuditoriaCuenta.accion == "REEMISION_CREDENCIAL").count(), 1)
        db.close()

    def test_produccion_exige_secreto_fuerte_y_credencial_aleatoria(self):
        with self.assertRaises(RuntimeError):
            validate_security_settings("production", None, "random")
        with self.assertRaises(RuntimeError):
            validate_security_settings("production", "x" * 40, "documento")
        self.assertEqual(validate_security_settings("production", "x" * 40, "random"), "x" * 40)


if __name__ == "__main__":
    unittest.main()
