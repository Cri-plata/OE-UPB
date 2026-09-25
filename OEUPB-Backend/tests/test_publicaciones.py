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
        db.flush()
        coord1 = next(u for u in usuarios if u.correo == "coord1@upb.edu.co")
        carga = Carga(nombre_archivo="s1.xlsx", hash_archivo="a" * 64, usuario_id=coord1.id, sede_id=1, momento=0, anio_grado=2025, estado="vigente", version=1, registros=7)
        db.add(carga)
        db.flush()
        # Seis egresados de Derecho responden "SI" y uno de Medicina responde "NO".
        for indice in range(7):
            documento = str(100 + indice)
            programa, respuesta = ("Derecho", "SI") if indice < 6 else ("Medicina", "NO")
            db.add(Egresado(numero_documento=documento, primer_nombre=f"Egresado {indice}", programa=programa))
            db.flush()
            db.add(Medicion(
                carga_id=carga.id, egresado_documento=documento, momento=0, anio=2025, sede_id=1,
                respuestas={"NUMERO_DOCUMENTO": documento, "CORREO": f"e{indice}@mail.com", "¿Trabaja actualmente?": respuesta},
            ))
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
            # Campos heredados que el backend debe ignorar: no puede confiar en el cliente.
            "programas": ["Medicina", "Arquitectura"],
            "metricas": {"labels": ["Inventado"], "datasets": [{"label": "Egresados", "data": [valor]}]},
            "definicion": {"origen": "reporte_general", "tipo_visualizacion": "doughnut", "indicador": "distribucion_programas"},
            "aprobada_privacidad": aprobada,
        }

    @staticmethod
    def payload_explorador(pregunta="¿Trabaja actualmente?"):
        return {
            "grafica_key": "explorador_trabajo",
            "titulo": "Explorador: trabajo",
            "definicion": {"origen": "explorador", "tipo_visualizacion": "bar", "pregunta": pregunta},
            "aprobada_privacidad": True,
        }

    def test_publicacion_versionada_y_retiro_conservan_instantaneas(self):
        coord1 = self.login("coord1@upb.edu.co")
        primera = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload())
        self.assertEqual(primera.status_code, 201, primera.text)
        self.assertEqual(primera.json()["version"], 1)

        segunda = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload(valor=15))
        self.assertEqual(primera.json()["metricas"]["labels"], ["Derecho"])
        self.assertEqual(primera.json()["programas"], ["Derecho"])
        self.assertEqual(segunda.status_code, 201, segunda.text)
        self.assertEqual(segunda.json()["version"], 2)

        db = self.Session()
        versiones = db.query(PublicacionGrafica).order_by(PublicacionGrafica.version).all()
        self.assertEqual([(p.version, p.estado) for p in versiones], [(1, "reemplazada"), (2, "publicada")])
        # Medicina (1 egresado) queda suprimida por el umbral k>=5; el valor del cliente se ignora.
        self.assertEqual(versiones[0].metricas["datasets"][0]["data"], [6.0])
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

    def test_explorador_suprime_celdas_pequenas_y_rechaza_variables_personales(self):
        coord1 = self.login("coord1@upb.edu.co")
        init = self.client.get("/api/reportes/explorador/init", headers=coord1)
        self.assertEqual(init.status_code, 200, init.text)
        self.assertEqual(init.json()["preguntas"], ["¿Trabaja actualmente?"])

        privado = self.client.get("/api/reportes/explorador", headers=coord1, params={"pregunta": "¿Trabaja actualmente?"})
        self.assertEqual(privado.json(), {"labels": ["SI", "NO"], "valores": [6, 1]})
        for variable in ("NUMERO_DOCUMENTO", "CORREO"):
            rechazo = self.client.get("/api/reportes/explorador", headers=coord1, params={"pregunta": variable})
            self.assertEqual(rechazo.status_code, 422, variable)
            self.assertEqual(self.client.post("/api/publicaciones/", headers=coord1, json=self.payload_explorador(variable)).status_code, 422)

        publicada = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload_explorador())
        self.assertEqual(publicada.status_code, 201, publicada.text)
        self.assertEqual(publicada.json()["metricas"]["labels"], ["SI"])
        self.assertEqual(publicada.json()["metricas"]["datasets"][0]["data"], [6.0])

    def test_publicacion_sin_celdas_suficientes_se_rechaza(self):
        coord1 = self.login("coord1@upb.edu.co")
        payload = self.payload_explorador()
        payload["definicion"]["programa"] = "Medicina"
        respuesta = self.client.post("/api/publicaciones/", headers=coord1, json=payload)
        self.assertEqual(respuesta.status_code, 422, respuesta.text)

    def test_otro_coordinador_de_la_sede_retira_si_el_propietario_esta_inactivo(self):
        db = self.Session()
        db.add(Usuario(nombre="Coord 1b", correo="coord1b@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=1))
        db.commit()
        db.close()
        coord1 = self.login("coord1@upb.edu.co")
        coord1b = self.login("coord1b@upb.edu.co")
        creada = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload()).json()
        self.assertEqual(self.client.delete(f"/api/publicaciones/{creada['id']}", headers=coord1b).status_code, 403)

        db = self.Session()
        db.query(Usuario).filter(Usuario.correo == "coord1@upb.edu.co").one().activo = False
        db.commit()
        db.close()
        retiro = self.client.delete(f"/api/publicaciones/{creada['id']}", headers=coord1b)
        self.assertEqual(retiro.status_code, 200, retiro.text)

    def test_ciclo_publicar_consultar_retirar_para_consulta(self):
        coord1 = self.login("coord1@upb.edu.co")
        profesor = self.login("profesor@upb.edu.co")
        self.assertEqual(self.client.get("/api/publicaciones/", headers=profesor).json(), [])

        creada = self.client.post("/api/publicaciones/", headers=coord1, json=self.payload())
        self.assertEqual(creada.status_code, 201, creada.text)
        catalogo = self.client.get("/api/publicaciones/", headers=profesor).json()
        self.assertEqual([p["id"] for p in catalogo], [creada.json()["id"]])
        self.assertEqual(len(self.client.get("/api/publicaciones/mias", headers=coord1).json()), 1)
        # El catálogo no expone datos fuente: solo etiquetas y métricas agregadas.
        self.assertNotIn("respuestas", catalogo[0])
        self.assertNotIn("100", str(catalogo[0]["metricas"]))

        self.assertEqual(self.client.delete(f"/api/publicaciones/{creada.json()['id']}", headers=coord1).status_code, 200)
        self.assertEqual(self.client.get("/api/publicaciones/", headers=profesor).json(), [])
        self.assertEqual(self.client.get("/api/publicaciones/mias", headers=coord1).json(), [])
        self.assertEqual(self.client.delete(f"/api/publicaciones/{creada.json()['id']}", headers=coord1).status_code, 409)


if __name__ == "__main__":
    unittest.main()
