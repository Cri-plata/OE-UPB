"""Diccionario DIVIPOLA para las preguntas de ubicación (departamento y municipio)."""

import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from application.divipola import (
    describir_ubicacion,
    nombre_departamento,
    nombre_municipio,
    normalizar_codigo_departamento,
    normalizar_codigo_municipio,
    tipo_columna_ubicacion,
)
from domain.models import Base, Carga, Egresado, Medicion, Sede, Usuario
from infrastructure.database import get_db
from main import app

CLAVE = "ClaveSegura2026"
PREGUNTA_MUNICIPIO = "Pregunta 52: ¿Cuál es su lugar de residencia actual? (MUNICIPIO)"
PREGUNTA_DEPARTAMENTO = "Pregunta 52: ¿Cuál es su lugar de residencia actual? (DEPARTAMENTO)"


class DiccionarioDivipolaTest(unittest.TestCase):
    def test_normaliza_codigos_que_perdieron_el_cero_inicial(self):
        # Excel convierte "05" en 5 y "05001" en 5001; también puede agregar ".0".
        self.assertEqual(normalizar_codigo_departamento(5), "05")
        self.assertEqual(normalizar_codigo_departamento("68.0"), "68")
        self.assertEqual(normalizar_codigo_municipio(5001), "05001")
        self.assertEqual(normalizar_codigo_municipio("68001.0"), "68001")
        self.assertIsNone(normalizar_codigo_municipio("BUCARAMANGA"))
        self.assertIsNone(normalizar_codigo_municipio("123"))

    def test_nombres_legibles(self):
        self.assertEqual(nombre_departamento("68"), "Santander")
        self.assertEqual(nombre_departamento(5), "Antioquia")
        self.assertEqual(nombre_municipio("68001"), "Bucaramanga")
        self.assertEqual(nombre_municipio(5148), "El Carmen de Viboral")
        self.assertEqual(nombre_municipio("11001"), "Bogotá, D.C.")
        self.assertEqual(nombre_municipio("13490"), "Norosí")  # complemento posterior a 2007
        self.assertIsNone(nombre_municipio("99999"))
        self.assertIsNone(nombre_departamento("00"))

    def test_detecta_columnas_de_ubicacion(self):
        self.assertEqual(tipo_columna_ubicacion(PREGUNTA_MUNICIPIO), "municipio")
        self.assertEqual(tipo_columna_ubicacion(PREGUNTA_DEPARTAMENTO), "departamento")
        self.assertIsNone(tipo_columna_ubicacion("Pregunta 52: ¿Cuál es su lugar de residencia actual? (PAIS)"))
        self.assertIsNone(tipo_columna_ubicacion("¿Trabaja actualmente?"))

    def test_describe_valores_y_conserva_los_desconocidos(self):
        self.assertEqual(describir_ubicacion(PREGUNTA_MUNICIPIO, "68001"), "Bucaramanga (Santander)")
        self.assertEqual(describir_ubicacion(PREGUNTA_MUNICIPIO, 5001), "Medellín (Antioquia)")
        self.assertEqual(describir_ubicacion(PREGUNTA_DEPARTAMENTO, 68), "Santander")
        # Si el municipio ya nombra a su departamento, no se repite entre paréntesis.
        self.assertEqual(describir_ubicacion(PREGUNTA_MUNICIPIO, "11001"), "Bogotá, D.C.")
        self.assertEqual(describir_ubicacion(PREGUNTA_MUNICIPIO, "88001"), "San Andrés")
        # Un código que no está en el diccionario no se inventa: se conserva tal cual.
        self.assertEqual(describir_ubicacion(PREGUNTA_MUNICIPIO, "99999"), "99999")
        self.assertEqual(describir_ubicacion(PREGUNTA_DEPARTAMENTO, "00"), "00")
        # Una columna que no es de ubicación no se modifica.
        self.assertEqual(describir_ubicacion("¿Trabaja actualmente?", "68001"), "68001")


class UbicacionEnApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()
        db.add(Sede(id=1, codigo="BUC", nombre="Bucaramanga"))
        coord = Usuario(nombre="Coord", correo="coord@upb.edu.co", contrasena_hash=get_password_hash(CLAVE), rol="Coordinador_Sede", sede_id=1)
        db.add(coord)
        db.flush()
        carga = Carga(nombre_archivo="m0.xlsx", hash_archivo="d" * 64, usuario_id=coord.id, sede_id=1, momento=0,
                      anio_grado=2024, estado="vigente", version=1, registros=7)
        db.add(carga)
        db.flush()
        # Seis residen en Bucaramanga (código con y sin ".0") y uno en Medellín (código sin cero inicial).
        for i, (municipio, depto) in enumerate([("68001", 68)] * 3 + [("68001.0", 68)] * 3 + [(5001, 5)]):
            documento = str(900000 + i)
            db.add(Egresado(numero_documento=documento, primer_nombre=f"E{i}", programa="Derecho"))
            db.flush()
            db.add(Medicion(carga_id=carga.id, egresado_documento=documento, momento=0, anio=2024, sede_id=1,
                            respuestas={PREGUNTA_MUNICIPIO: municipio, PREGUNTA_DEPARTAMENTO: depto}))
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
        token = self.client.post("/api/auth/login", json={"correoInstitucional": "coord@upb.edu.co", "contrasena": CLAVE}).json()["token"]
        self.headers = {"Authorization": f"Bearer {token}"}

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_explorador_muestra_nombres_de_municipio(self):
        respuesta = self.client.get("/api/reportes/explorador", params={"pregunta": PREGUNTA_MUNICIPIO}, headers=self.headers)
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        datos = dict(zip(respuesta.json()["labels"], respuesta.json()["valores"]))
        # "68001" y "68001.0" se agrupan en una sola categoría.
        self.assertEqual(datos, {"Bucaramanga (Santander)": 6, "Medellín (Antioquia)": 1})

    def test_explorador_muestra_nombres_de_departamento(self):
        respuesta = self.client.get("/api/reportes/explorador", params={"pregunta": PREGUNTA_DEPARTAMENTO}, headers=self.headers)
        self.assertEqual(dict(zip(respuesta.json()["labels"], respuesta.json()["valores"])), {"Santander": 6, "Antioquia": 1})

    def test_publicacion_usa_nombres_y_respeta_el_umbral(self):
        payload = {
            "grafica_key": "explorador_residencia",
            "titulo": "Explorador: residencia actual",
            "definicion": {"origen": "explorador", "tipo_visualizacion": "bar", "pregunta": PREGUNTA_MUNICIPIO},
            "aprobada_privacidad": True,
        }
        respuesta = self.client.post("/api/publicaciones/", json=payload, headers=self.headers)
        self.assertEqual(respuesta.status_code, 201, respuesta.text)
        # Medellín (1 observación) queda suprimido por k = 5; Bucaramanga se publica con su nombre.
        self.assertEqual(respuesta.json()["metricas"]["labels"], ["Bucaramanga (Santander)"])

    def test_ficha_del_egresado_describe_la_ubicacion(self):
        respuesta = self.client.get("/api/directorio/perfil/900006", headers=self.headers)
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        respuestas = respuesta.json()["encuestas"][0]["respuestas_completas"]
        self.assertEqual(respuestas[PREGUNTA_MUNICIPIO], "Medellín (Antioquia)")
        self.assertEqual(respuestas[PREGUNTA_DEPARTAMENTO], "Antioquia")


if __name__ == "__main__":
    unittest.main()
