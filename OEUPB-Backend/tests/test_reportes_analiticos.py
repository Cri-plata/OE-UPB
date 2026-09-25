import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from application.indicadores import ETIQUETA_OTROS, estado_laboral, extraer_salario, formalidad, salario
from domain.models import Base, Carga, Egresado, Medicion, Sede, Usuario
from infrastructure.database import get_db
from main import app

# Nombres de columna tal como llegan en los cuestionarios OLE.
M1_REMUNERADA = "Pregunta 22: En la actualidad, ¿realiza alguna actividad remunerada?"
M1_POSICION = "Pregunta 57: En la actividad remunerada que usted realiza actualmente es:"
M1_CONTRATO = "Pregunta 59: ¿Qué tipo de contrato tiene?"
M0_TRABAJA = "Pregunta 17: En este momento aparte de estudiar, ¿usted se dedica a trabajar o está en proceso de creación de una empresa o negocio particular?"
M0_POSICION = "Pregunta 25: ¿En este trabajo usted es?"
M0_INGRESO = "Pregunta 20: ¿Cuál es su ingreso mensual (en cantidad de salarios mínimos mensuales legales vigentes - SMMLV) asociado a la actividad o trabajo que realiza?"


class TaxonomiaLaboralTest(unittest.TestCase):
    def test_clasifica_seguimiento(self):
        self.assertEqual(estado_laboral({M1_REMUNERADA: "NO"}), "sin_empleo")
        self.assertEqual(estado_laboral({M1_REMUNERADA: "SI", M1_POSICION: "Empleado"}), "empleado")
        self.assertEqual(estado_laboral({M1_REMUNERADA: "SI", M1_POSICION: "Contratista por prestación de servicios o cuenta propia"}), "independiente")
        self.assertEqual(estado_laboral({M1_REMUNERADA: "SI", M1_POSICION: "Propietario de una empresa o negocio particular"}), "independiente")
        self.assertIsNone(estado_laboral({M1_REMUNERADA: "SI", M1_POSICION: None}))
        self.assertIsNone(estado_laboral({M1_REMUNERADA: None}))

    def test_clasifica_momento_cero(self):
        self.assertEqual(estado_laboral({M0_TRABAJA: "No"}), "estudiante")
        self.assertEqual(estado_laboral({M0_TRABAJA: "Si", M0_POSICION: "Empleado/Trabajador dependiente"}), "empleado")
        self.assertEqual(estado_laboral({M0_TRABAJA: "Si", M0_POSICION: "Trabaja en una empresa o negocio familiar"}), "empleado")
        self.assertEqual(estado_laboral({M0_TRABAJA: "Si", M0_POSICION: "Trabajador independiente"}), "independiente")
        self.assertEqual(estado_laboral({M0_TRABAJA: "Si", M0_POSICION: "Practicante/Pasante"}), "estudiante")
        self.assertIsNone(estado_laboral({}))

    def test_formalidad_solo_en_seguimiento(self):
        self.assertEqual(formalidad({M1_REMUNERADA: "SI", M1_POSICION: "Empleado", M1_CONTRATO: "Contrato a término indefinido"}), "formal")
        self.assertIsNone(formalidad({M1_REMUNERADA: "SI", M1_POSICION: "Empleado", M1_CONTRATO: None}))
        self.assertEqual(formalidad({M1_REMUNERADA: "SI", M1_POSICION: "Contratista por prestación de servicios o cuenta propia"}), "no_formal")
        self.assertIsNone(formalidad({M0_TRABAJA: "Si", M0_POSICION: "Trabajador independiente"}))

    def test_salario_reconoce_smmlv_y_punto_medio(self):
        self.assertEqual(extraer_salario("Entre 1 y 2 SMMLV"), 1.5)
        self.assertEqual(extraer_salario("Entre 1 y 1,5 SMLV"), 1.25)
        self.assertEqual(salario({M0_INGRESO: "Entre 2 y 3 SMMLV"}), 2.5)


class ReportesAnaliticosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()
        db.add_all([Sede(id=1, codigo="BUC", nombre="Bucaramanga"), Sede(id=2, codigo="MED", nombre="Medellín")])
        coordinador = Usuario(nombre="Coord", correo="coord@upb.edu.co", contrasena_hash=get_password_hash("ClaveSegura2026"), rol="Coordinador_Sede", sede_id=1)
        db.add(coordinador)
        db.flush()
        cargas = {}
        for momento in (0, 1):
            cargas[momento] = Carga(nombre_archivo=f"m{momento}.xlsx", hash_archivo=str(momento) * 64, usuario_id=coordinador.id, sede_id=1, momento=momento, anio_grado=2024, estado="vigente", version=1, registros=0)
            db.add(cargas[momento])
        otra = Carga(nombre_archivo="otra.xlsx", hash_archivo="9" * 64, usuario_id=coordinador.id, sede_id=2, momento=1, anio_grado=2024, estado="vigente", version=1, registros=0)
        db.add(otra)
        db.flush()
        # Derecho: 6 egresados; en M0 todos estudian y en M1 5 trabajan (4 con contrato) y 1 no.
        for indice in range(6):
            documento = f"DER{indice:04d}"
            db.add(Egresado(numero_documento=documento, primer_nombre="E", programa="Derecho"))
            db.flush()
            db.add(Medicion(carga_id=cargas[0].id, egresado_documento=documento, momento=0, anio=2024, sede_id=1,
                            respuestas={M0_TRABAJA: "No", M0_INGRESO: None}))
            m1 = {M1_REMUNERADA: "SI", M1_POSICION: "Empleado", M1_CONTRATO: "Contrato a término indefinido"} if indice < 4 else (
                {M1_REMUNERADA: "SI", M1_POSICION: "Contratista por prestación de servicios o cuenta propia"} if indice == 4 else {M1_REMUNERADA: "NO"})
            db.add(Medicion(carga_id=cargas[1].id, egresado_documento=documento, momento=1, anio=2024, sede_id=1, respuestas=m1))
        # Medicina: 2 egresados solo en M0, trabajando; y un dato de otra sede que nunca debe contarse.
        for indice in range(2):
            documento = f"MED{indice:04d}"
            db.add(Egresado(numero_documento=documento, primer_nombre="E", programa="Medicina"))
            db.flush()
            db.add(Medicion(carga_id=cargas[0].id, egresado_documento=documento, momento=0, anio=2023, sede_id=1,
                            respuestas={M0_TRABAJA: "Si", M0_POSICION: "Empleado/Trabajador dependiente", M0_INGRESO: "Entre 2 y 3 SMMLV"}))
        db.add(Egresado(numero_documento="AJENO0001", primer_nombre="E", programa="Derecho"))
        db.flush()
        db.add(Medicion(carga_id=otra.id, egresado_documento="AJENO0001", momento=1, anio=2024, sede_id=2, respuestas={M1_REMUNERADA: "NO"}))
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
        respuesta = self.client.post("/api/auth/login", json={"correoInstitucional": "coord@upb.edu.co", "contrasena": "ClaveSegura2026"})
        self.headers = {"Authorization": f"Bearer {respuesta.json()['token']}"}

    def tearDown(self):
        app.dependency_overrides.clear()

    def get(self, ruta, **params):
        return self.client.get(ruta, headers=self.headers, params=params)

    def test_kpis_con_taxonomia_formalidad_y_rango(self):
        kpis = self.get("/api/reportes/general").json()
        self.assertEqual(kpis["distribucion_estado_laboral"], {"empleado": 6, "independiente": 1, "estudiante": 6, "sin_empleo": 1})
        self.assertEqual(kpis["total_encuestados"], 14)
        self.assertEqual(kpis["total_egresados"], 8)
        self.assertEqual(kpis["tasa_empleabilidad"], 50.0)  # 7 ocupados / 14 clasificados
        self.assertEqual(kpis["tasa_formalidad"], 80.0)  # 4 formales / 5 con formalidad (M1)
        self.assertEqual(kpis["tasa_informalidad"], 20.0)
        self.assertEqual(kpis["rango_salarial"], {"minimo": 2.5, "mediana": 2.5, "maximo": 2.5, "observaciones": 2})

    def test_kpis_filtran_por_programas_cohortes_y_momento(self):
        solo_medicina = self.get("/api/reportes/general", programas=["Medicina"]).json()
        self.assertEqual(solo_medicina["total_egresados"], 2)
        self.assertEqual(solo_medicina["distribucion_programas"], {"Medicina": 2})
        cohorte = self.get("/api/reportes/general", anios=[2024], momento=1).json()
        self.assertEqual(cohorte["distribucion_estado_laboral"], {"empleado": 4, "independiente": 1, "estudiante": 0, "sin_empleo": 1})
        self.assertEqual(self.get("/api/reportes/general", momento=3).status_code, 422)

    def test_filtros_disponibles_de_la_sede(self):
        self.assertEqual(self.get("/api/reportes/filtros").json(), {"programas": ["Derecho", "Medicina"], "anios": [2023, 2024], "momentos": [0, 1]})

    def test_comparacion_usa_pares_de_la_misma_cohorte_y_minimo(self):
        comparacion = self.get("/api/reportes/comparacion", momento_inicial=0, momento_final=1).json()
        self.assertEqual(comparacion["minimo_pares"], 5)
        self.assertEqual(comparacion["programas"], [
            {"programa": "Derecho", "pares": 6, "suficiente": True, "valor_inicial": 0.0, "valor_final": 83.3},
        ])
        insuficiente = self.get("/api/reportes/comparacion", momento_inicial=0, momento_final=1, programas=["Derecho"], anios=[2023]).json()
        self.assertEqual(insuficiente["programas"], [])
        self.assertEqual(self.get("/api/reportes/comparacion", momento_inicial=1, momento_final=1).status_code, 422)

    def test_tendencias_filtran_programas(self):
        tendencias = self.get("/api/reportes/tendencias", indicador="empleabilidad", programas=["Derecho"]).json()
        self.assertEqual([d["label"] for d in tendencias["datasets"]], ["Derecho"])
        self.assertEqual(tendencias["datasets"][0]["data"], [0.0, 83.3, None])

    def test_publicacion_respeta_filtros_y_umbral(self):
        payload = {
            "grafica_key": "reporte_general_estado_laboral",
            "titulo": "Estado laboral",
            "definicion": {"origen": "reporte_general", "tipo_visualizacion": "bar", "indicador": "estado_laboral", "programas": ["Derecho"]},
            "aprobada_privacidad": True,
        }
        publicada = self.client.post("/api/publicaciones/", headers=self.headers, json=payload)
        self.assertEqual(publicada.status_code, 201, publicada.text)
        self.assertEqual(publicada.json()["programas"], ["Derecho"])
        # Estudiante (6) supera k; empleado (4), independiente (1) y sin empleo (1) se agrupan (6 >= k).
        metricas = publicada.json()["metricas"]
        self.assertEqual(dict(zip(metricas["labels"], metricas["datasets"][0]["data"])), {"Estudiante": 6.0, ETIQUETA_OTROS: 6.0})


if __name__ == "__main__":
    unittest.main()
