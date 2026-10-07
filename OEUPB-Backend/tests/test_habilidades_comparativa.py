"""
Pruebas de la Comparativa Temporal Longitudinal de Habilidades (IA-06).
"""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from infrastructure.database import Base, get_db
from domain.models import Sede, Usuario, Egresado, Medicion, Carga
from application.auth_service import create_access_token
from application.ia_service import comparar_habilidades_temporales


class TestHabilidadesComparativa(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()

        sede = Sede(id=1, codigo="BUC", nombre="Bucaramanga")
        db.add(sede)

        coordinador = Usuario(
            nombre="Coordinador Comparativa",
            correo="coord_comp@upb.edu.co",
            contrasena_hash="fakehash",
            rol="Coordinador_Sede",
            sede_id=1,
            activo=True,
            version_autorizacion=1,
        )
        db.add(coordinador)
        db.flush()

        carga = Carga(
            nombre_archivo="test.xlsx",
            hash_archivo="0" * 64,
            usuario_id=coordinador.id,
            sede_id=1,
            momento=0,
            anio_grado=2023,
            estado="vigente",
            version=1,
            registros=2,
        )
        db.add(carga)
        db.flush()

        # Crear egresados y mediciones para M0, M1, M5
        egresado1 = Egresado(numero_documento="1001", primer_nombre="Ana", programa="Ingeniería de Sistemas")
        egresado2 = Egresado(numero_documento="1002", primer_nombre="Beto", programa="Ingeniería de Sistemas")
        db.add_all([egresado1, egresado2])

        # Respuestas con preguntas abiertas simuladas
        m0_1 = Medicion(
            carga_id=carga.id,
            egresado_documento="1001",
            sede_id=1,
            momento=0,
            anio=2023,
            respuestas={"principal tarea que usted realiza": "Gestión de proyectos y liderazgo de equipos"}
        )
        m1_1 = Medicion(
            carga_id=carga.id,
            egresado_documento="1001",
            sede_id=1,
            momento=1,
            anio=2024,
            respuestas={"describa brevemente la principal tarea": "Gestión de proyectos y arquitectura en la nube con Python"}
        )
        m5_1 = Medicion(
            carga_id=carga.id,
            egresado_documento="1001",
            sede_id=1,
            momento=5,
            anio=2025,
            respuestas={"aspectos a mejorar": "Gestión de proyectos estratégicos y machine learning"}
        )
        db.add_all([m0_1, m1_1, m5_1])
        db.commit()

        self.coord_token = create_access_token({
            "sub": coordinador.correo,
            "usuario_id": coordinador.id,
            "rol": coordinador.rol,
            "sede_id": coordinador.sede_id,
            "version_autorizacion": coordinador.version_autorizacion,
        })
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

    def test_logica_comparativa_temporales(self):
        textos = {
            0: ["Requiere liderazgo y trabajo en equipo", "Liderazgo de proyectos"],
            1: ["Exige liderazgo, trabajo en equipo y python", "Desarrollo con python y machine learning"],
            5: ["Dirección ejecutiva, machine learning y python"],
        }
        res = comparar_habilidades_temporales(textos, top_n=10)
        self.assertIn("comparativa", res)
        self.assertIn("totales_respuestas", res)
        self.assertEqual(res["totales_respuestas"][0], 2)
        self.assertEqual(res["totales_respuestas"][1], 2)
        self.assertEqual(res["totales_respuestas"][5], 1)

        items = {row["habilidad"]: row for row in res["comparativa"]}
        self.assertTrue(len(items) > 0)
        
        # Verificar presencia de campos de porcentaje duales
        for row in res["comparativa"]:
            self.assertIn("m0_pct", row)
            self.assertIn("m0_porcentaje", row)
            self.assertEqual(row["m0_pct"], row["m0_porcentaje"])
            self.assertIn("tendencia", row)

    def test_endpoint_habilidades_comparativa_autorizado(self):
        response = self.client.get(
            "/api/ia/habilidades-comparativa?top_n=20",
            headers={"Authorization": f"Bearer {self.coord_token}"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("comparativa", data)
        self.assertIn("totales_respuestas", data)
        self.assertIn("totales_con_habilidad", data)
        self.assertIsInstance(data["comparativa"], list)

    def test_endpoint_habilidades_comparativa_sin_auth(self):
        response = self.client.get("/api/ia/habilidades-comparativa")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
