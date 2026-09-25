"""Pruebas de la sección P3 del backlog: API-02, PRG-01 y ANA-02."""
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from application.programas import clave_programa, limpiar_nombre_programa
from domain.models import Base, Carga, Egresado, Medicion, PublicacionGrafica, Sede, Usuario
from infrastructure.database import get_db
from main import app
from presentation.analitica_router import alertas_de_programas

M1_REMUNERADA = "Pregunta 22: En la actualidad, ¿realiza alguna actividad remunerada?"
M1_POSICION = "Pregunta 57: En la actividad remunerada que usted realiza actualmente es:"
M0_TRABAJA = "Pregunta 17: En este momento aparte de estudiar, ¿usted se dedica a trabajar o está en proceso de creación de una empresa o negocio particular?"
PUBLICAS = {"/", "/api/auth/login", "/api/health/live", "/api/health/ready"}


class ContratoErroresTest(unittest.TestCase):
    def test_rutas_protegidas_declaran_401_y_403_con_detail(self):
        contrato = app.openapi()
        esquema = contrato["components"]["schemas"]["ErrorResponse"]
        self.assertIn("detail", esquema["properties"])
        for ruta, operaciones in contrato["paths"].items():
            if ruta in PUBLICAS or ruta.startswith("/api/auth/"):
                continue
            for metodo, operacion in operaciones.items():
                for codigo in ("401", "403"):
                    with self.subTest(ruta=ruta, metodo=metodo, codigo=codigo):
                        respuesta = operacion["responses"].get(codigo)
                        self.assertIsNotNone(respuesta)
                        self.assertIn("ErrorResponse", str(respuesta["content"]))

    def test_errores_especificos_y_alias_obsoleto(self):
        paths = app.openapi()["paths"]
        self.assertIn("404", paths["/api/directorio/perfil/{documento}"]["get"]["responses"])
        self.assertIn("409", paths["/api/publicaciones/{publicacion_id}"]["delete"]["responses"])
        self.assertIn("409", paths["/api/usuarios/{usuario_id}/permanente"]["delete"]["responses"])
        self.assertTrue(paths["/api/usuarios/{usuario_id}"]["delete"].get("deprecated"))
        correo = app.openapi()["components"]["schemas"]["UsuarioCreateRequest"]["properties"]["correo"]
        self.assertIn("[Uu][Pp][Bb]", correo["pattern"])


class ProgramasTest(unittest.TestCase):
    def test_clave_ignora_mayusculas_tildes_y_espacios(self):
        self.assertEqual(clave_programa("  Ingeniería   de Sistemas "), clave_programa("ingenieria de sistemas"))
        self.assertNotEqual(clave_programa("Derecho"), clave_programa("Medicina"))
        self.assertEqual(limpiar_nombre_programa("  Derecho   Penal "), "Derecho Penal")
        self.assertIsNone(limpiar_nombre_programa("   "))


class AlertasTest(unittest.TestCase):
    def test_umbrales_severidad_y_muestra_minima(self):
        empleo = {
            ("Derecho", 1): {"ocupados": 2, "clasificados": 5},      # 40 % -> alta
            ("Medicina", 1): {"ocupados": 3, "clasificados": 5},     # 60 % -> media
            ("Arquitectura", 1): {"ocupados": 4, "clasificados": 5}, # 80 % -> sin alerta
            ("Psicologia", 5): {"ocupados": 0, "clasificados": 4},   # muestra insuficiente
        }
        textos = {"Derecho": {"negativos": 3, "textos": 5}, "Medicina": {"negativos": 3, "textos": 4}}
        alertas = alertas_de_programas(empleo, textos)
        resumen = [(a["tipo"], a["programa"], a["momento"], a["severidad"]) for a in alertas]
        self.assertEqual(resumen, [
            ("empleabilidad", "Derecho", 1, "alta"),
            ("empleabilidad", "Medicina", 1, "media"),
            ("texto_abierto", "Derecho", None, "media"),
        ])


class IntegracionP3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()
        db.add_all([Sede(id=1, codigo="BUC", nombre="Bucaramanga"), Sede(id=2, codigo="MED", nombre="Medellín")])
        clave = get_password_hash("ClaveSegura2026")
        coord = Usuario(nombre="Coord", correo="coord@upb.edu.co", contrasena_hash=clave, rol="Coordinador_Sede", sede_id=1)
        db.add_all([
            coord,
            Usuario(nombre="Coord 2", correo="coord2@upb.edu.co", contrasena_hash=clave, rol="Coordinador_Sede", sede_id=2),
            # Programa asignado con otra grafía y uno que ya no se observa en cargas.
            Usuario(nombre="Profe", correo="profe@upb.edu.co", contrasena_hash=clave, rol="Usuario_Consulta", sede_id=2,
                    etiqueta="Profesor", permisos=["ver_publicaciones", "ver_reporte_general"], programas=["ingenieria de sistemas", "Programa Retirado"]),
        ])
        db.flush()
        carga = Carga(nombre_archivo="m.xlsx", hash_archivo="a" * 64, usuario_id=coord.id, sede_id=1, momento=1, anio_grado=2024, estado="vigente", version=1, registros=6)
        carga2 = Carga(nombre_archivo="n.xlsx", hash_archivo="b" * 64, usuario_id=coord.id, sede_id=2, momento=1, anio_grado=2024, estado="vigente", version=1, registros=1)
        db.add_all([carga, carga2])
        db.flush()
        for indice in range(6):
            documento = f"SIS{indice:04d}"
            db.add(Egresado(numero_documento=documento, primer_nombre="E", programa="Ingeniería de Sistemas"))
            db.flush()
            # 2 de 6 ocupados en M1 -> 33,3 % (alerta alta); en M0 no se evalúan alertas.
            respuestas = {M1_REMUNERADA: "SI", M1_POSICION: "Empleado"} if indice < 2 else {M1_REMUNERADA: "NO"}
            db.add(Medicion(carga_id=carga.id, egresado_documento=documento, momento=1, anio=2024, sede_id=1, respuestas=respuestas))
            db.add(Medicion(carga_id=carga.id, egresado_documento=documento, momento=0, anio=2024, sede_id=1, respuestas={M0_TRABAJA: "No"}))
        db.add(Egresado(numero_documento="SIS9999", primer_nombre="E", programa="ingenieria de sistemas"))
        db.flush()
        db.add(Medicion(carga_id=carga2.id, egresado_documento="SIS9999", momento=1, anio=2024, sede_id=2, respuestas={}))
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

    def login(self, correo):
        respuesta = self.client.post("/api/auth/login", json={"correoInstitucional": correo, "contrasena": "ClaveSegura2026"})
        return {"Authorization": f"Bearer {respuesta.json()['token']}"}

    def test_alertas_solo_en_seguimiento_con_taxonomia(self):
        alertas = self.client.get("/api/analitica/resumen", headers=self.login("coord@upb.edu.co")).json()["alertas"]
        self.assertEqual([(a["programa"], a["momento"], a["severidad"], a["valor"]) for a in alertas],
                         [("Ingeniería de Sistemas", 1, "alta", 33.3)])

    def test_audiencia_compara_programas_por_clave(self):
        coord = self.login("coord@upb.edu.co")
        payload = {"grafica_key": "reporte_general_distribucion_programas", "titulo": "Distribución",
                   "definicion": {"origen": "reporte_general", "tipo_visualizacion": "bar", "indicador": "distribucion_programas"},
                   "aprobada_privacidad": True}
        self.assertEqual(self.client.post("/api/publicaciones/", headers=coord, json=payload).status_code, 201)
        catalogo = self.client.get("/api/publicaciones/", headers=self.login("profe@upb.edu.co")).json()
        self.assertEqual([p["programas"] for p in catalogo], [["Ingeniería de Sistemas"]])

    def test_programa_sin_datos_se_conserva_y_se_informa(self):
        coord2 = self.login("coord2@upb.edu.co")
        usuarios = self.client.get("/api/usuarios/", headers=coord2).json()
        profe = next(u for u in usuarios if u["correo"] == "profe@upb.edu.co")
        self.assertEqual(profe["programas_sin_datos"], ["Programa Retirado"])

        editado = self.client.patch(f"/api/usuarios/{profe['id']}", headers=coord2, json={"nombre": "Profe editado"})
        self.assertEqual(editado.status_code, 200, editado.text)
        # Editar otro campo no exige volver a observar el programa retirado: se conserva.
        self.assertEqual(editado.json()["programas"], ["Programa Retirado", "ingenieria de sistemas"])

        nuevo = self.client.patch(f"/api/usuarios/{profe['id']}", headers=coord2, json={"programas": ["Inexistente"]})
        self.assertEqual(nuevo.status_code, 422)


if __name__ == "__main__":
    unittest.main()
