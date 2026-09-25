import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from domain.models import AuditoriaEgresado, Base, Sede, Usuario
from infrastructure.database import get_db
from main import app


class DirectorioManualTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        db = self.Session()
        db.add_all([Sede(id=1, codigo="BOG", nombre="Bogotá"), Sede(id=2, codigo="MED", nombre="Medellín")])
        db.add_all([Usuario(nombre="Bog", correo="bog@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=1), Usuario(nombre="Med", correo="med@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=2)])
        db.commit(); db.close()
        def override():
            session = self.Session()
            try: yield session
            finally: session.close()
        app.dependency_overrides[get_db] = override
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def login(self, correo):
        response = self.client.post("/api/auth/login", json={"correoInstitucional": correo, "contrasena": "ClaveSegura2026"})
        return {"Authorization": f"Bearer {response.json()['token']}"}

    def test_crud_auditado_y_aislado_por_sede(self):
        bog = self.login("bog@upb.edu.co")
        med = self.login("med@upb.edu.co")
        payload = {"numero_documento": "10.010-001", "primer_nombre": "Carlos", "primer_apellido": "Ruiz", "programa": "Derecho", "fecha_grado": "2025-06-01", "motivo": "Registro solicitado"}
        self.assertEqual(self.client.post("/api/directorio/egresados", headers=bog, json=payload).status_code, 201)
        self.assertEqual(self.client.get("/api/directorio/tabla", headers=bog).json()["total"], 1)
        self.assertEqual(self.client.get("/api/directorio/tabla", headers=med).json()["total"], 0)
        analitica = self.client.get("/api/analitica/resumen", headers=bog)
        self.assertEqual(analitica.status_code, 200)
        self.assertNotIn("respuestas", analitica.json())
        self.assertEqual(self.client.patch("/api/directorio/egresados/10010001", headers=bog, json={"programa": "Economía", "motivo": "Corrección aprobada"}).status_code, 200)
        excel = self.client.get("/api/directorio/exportar.xlsx", headers=bog)
        self.assertEqual(excel.status_code, 200)
        self.assertTrue(excel.content.startswith(b"PK"))
        self.assertEqual(self.client.request("DELETE", "/api/directorio/egresados/10.010.001", headers=bog, json={"motivo": "Registro duplicado"}).status_code, 200)
        db = self.Session()
        self.assertEqual([a.accion for a in db.query(AuditoriaEgresado).order_by(AuditoriaEgresado.id)], ["crear", "editar", "eliminar"])
        db.close()


if __name__ == "__main__": unittest.main()
