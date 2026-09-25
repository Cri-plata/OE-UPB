import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from domain.models import Base, Carga, Egresado, Medicion, PublicacionGrafica, Sede, Usuario
from infrastructure.database import get_db
from main import app


class PublicacionesTest(unittest.TestCase):
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
            Usuario(nombre="CTIC", correo="ctic@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Admin_CTIC"),
            Usuario(nombre="Coord 1", correo="coord1@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=1),
            Usuario(nombre="Coord 2", correo="coord2@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=2),
            Usuario(nombre="Profesor", correo="profesor@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Usuario_Consulta", sede_id=2, etiqueta="Profesor", permisos=["ver_publicaciones", "ver_reporte_general"], programas=["Derecho"]),
            Usuario(nombre="Sin permiso", correo="sinpermiso@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Usuario_Consulta", sede_id=2, etiqueta="Profesor", permisos=["ver_publicaciones"], programas=["Derecho"]),
            Usuario(nombre="Otro programa", correo="otroprograma@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Usuario_Consulta", sede_id=2, etiqueta="Profesor", permisos=["ver_publicaciones", "ver_reporte_general"], programas=["Medicina"]),
        ]
        db.add_all(usuarios)
        db.add(Egresado(numero_documento="123", primer_nombre="Ana", programa="Derecho"))
        db.flush()
        coord1 = next(u for u in usuarios if u.correo == "coord1@upb.edu.co")
        carga = Carga(nombre_archivo="s1.xlsx", hash_archivo="a" * 64, usuario_id=coord1.id, sede_id=1, momento=0, anio_grado=2025, estado="vigente", version=1, registros=1)
        db.add(carga)
        db.flush()
        db.add(Medicion(carga_id=carga.id, egresado_documento="123", momento=0, anio=2025, sede_id=1, respuestas={}))
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

    def login(self, correo: str) -> dict:
        respuesta = self.client.post("/api/auth/login", json={"correoInstitucional": correo, "contrasena": "ClaveSegura2026"})
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        return {"Authorization": f"Bearer {respuesta.json()['token']}"}

    @staticmethod
    def payload(aprobada=True, valor=12):
        return {
            "grafica_key": "reporte_general_distribucion_programas",
            "titulo": "Distribución por programa",
            "programas": ["Derecho"],
            "definicion": {"origen": "reporte_general", "tipo_visualizacion": "doughnut"},
            "metricas": {"labels": ["Derecho"], "datasets": [{"label": "Egresados", "data": [valor]}]},
            "aprobada_privacidad": aprobada,
        }

    def test_publicacion_versionada_y_retiro_conservan_instantaneas(self):
        coord1 = self.login("coord1@upb.edu.co")
        primera = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload())
        self.assertEqual(primera.status_code, 201, primera.text)
        self.assertEqual(primera.json()["version"], 1)

        segunda = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload(valor=15))
        self.assertEqual(segunda.status_code, 201, segunda.text)
        self.assertEqual(segunda.json()["version"], 2)

        db = self.Session()
        versiones = db.query(PublicacionGrafica).order_by(PublicacionGrafica.version).all()
        self.assertEqual([(p.version, p.estado) for p in versiones], [(1, "reemplazada"), (2, "publicada")])
        self.assertEqual(versiones[0].metricas["datasets"][0]["data"], [12.0])
        db.close()

        retiro = self.client.delete(f"/api/publicaciones/{segunda.json()['id']}", headers=coord1)
        self.assertEqual(retiro.status_code, 200, retiro.text)
        self.assertEqual(retiro.json()["estado"], "retirada")
        self.assertEqual(self.client.get("/api/publicaciones/", headers=self.login("coord2@upb.edu.co")).json(), [])

    def test_audiencia_exige_permiso_y_programa(self):
        coord1 = self.login("coord1@upb.edu.co")
        creada = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload())
        self.assertEqual(creada.status_code, 201, creada.text)

        self.assertEqual(len(self.client.get("/api/publicaciones/", headers=self.login("coord2@upb.edu.co")).json()), 1)
        self.assertEqual(len(self.client.get("/api/publicaciones/", headers=self.login("profesor@upb.edu.co")).json()), 1)
        self.assertEqual(self.client.get("/api/publicaciones/", headers=self.login("sinpermiso@upb.edu.co")).json(), [])
        self.assertEqual(self.client.get("/api/publicaciones/", headers=self.login("otroprograma@upb.edu.co")).json(), [])
        self.assertEqual(self.client.get("/api/publicaciones/", headers=self.login("ctic@upb.edu.co")).status_code, 403)

    def test_solo_propietario_publica_y_retira_con_aprobacion(self):
        coord1 = self.login("coord1@upb.edu.co")
        coord2 = self.login("coord2@upb.edu.co")
        consulta = self.login("profesor@upb.edu.co")
        self.assertEqual(self.client.post("/api/publicaciones/", headers=coord1, json=self.payload(False)).status_code, 422)
        self.assertEqual(self.client.post("/api/publicaciones/", headers=consulta, json=self.payload()).status_code, 403)
        creada = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload())
        self.assertEqual(creada.status_code, 201, creada.text)
        self.assertEqual(self.client.delete(f"/api/publicaciones/{creada.json()['id']}", headers=coord2).status_code, 403)


if __name__ == "__main__":
    unittest.main()
