"""Alcance del módulo de IA: sede propia, curaduría por autor y anonimización (auditoría 07, ADR-020)."""

import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from application.ia_service import extraer_habilidades_por_respuesta, invalidar_cache_taxonomia, sincronizar_curadurias_bd
from domain.models import Base, Carga, Egresado, HabilidadCurada, Medicion, Sede, Usuario
from infrastructure.database import get_db
from main import app
from presentation.ia_router import _extraer_textos_libres

CLAVE = "ClaveSegura2026"


class IaAlcanceTest(unittest.TestCase):
    # Base en memoria: las pruebas nunca deben escribir en la base configurada en .env.

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()
        db.add_all([Sede(id=1, codigo="BUC", nombre="Bucaramanga"), Sede(id=2, codigo="MED", nombre="Medellín")])
        db.add_all([
            Usuario(nombre="CTIC", correo="ctic@upb.edu.co", contrasena_hash=get_password_hash(CLAVE), rol="Admin_CTIC"),
            Usuario(nombre="Coord 1", correo="coord1@upb.edu.co", contrasena_hash=get_password_hash(CLAVE), rol="Coordinador_Sede", sede_id=1),
            Usuario(nombre="Coord 2", correo="coord2@upb.edu.co", contrasena_hash=get_password_hash(CLAVE), rol="Coordinador_Sede", sede_id=2),
        ])
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
        invalidar_cache_taxonomia()

    def login(self, correo: str) -> dict:
        respuesta = self.client.post("/api/auth/login", json={"correoInstitucional": correo, "contrasena": CLAVE})
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        return {"Authorization": f"Bearer {respuesta.json()['token']}"}

    def curar(self, headers: dict, estado: str = "aprobada"):
        return self.client.post(
            "/api/ia/habilidades/curar",
            headers=headers,
            json={"termino_original": "kubernetes_alcance", "etiqueta_canonica": "Kubernetes", "tipo": "dura", "estado": estado},
        )

    def test_benchmark_solo_coordinador_y_sede_propia(self):
        self.assertEqual(self.client.get("/api/ia/prediccion-benchmark-sedes", headers=self.login("ctic@upb.edu.co")).status_code, 403)
        respuesta = self.client.get("/api/ia/prediccion-benchmark-sedes", headers=self.login("coord1@upb.edu.co"))
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        self.assertTrue(all(item["sede_id"] == 1 for item in respuesta.json()))

    def test_admin_ctic_no_cura_ni_consulta_curadurias(self):
        ctic = self.login("ctic@upb.edu.co")
        self.assertEqual(self.curar(ctic).status_code, 403)
        self.assertEqual(self.client.get("/api/ia/habilidades/curadas", headers=ctic).status_code, 403)

    def test_solo_el_autor_modifica_o_revierte_su_curaduria(self):
        coord1, coord2 = self.login("coord1@upb.edu.co"), self.login("coord2@upb.edu.co")
        creada = self.curar(coord1)
        self.assertEqual(creada.status_code, 200, creada.text)
        self.assertEqual(creada.json()["curada"]["creado_por_correo"], "coord1@upb.edu.co")

        self.assertEqual(self.curar(coord2, estado="descartada").status_code, 409)
        curada_id = creada.json()["curada"]["id"]
        self.assertEqual(self.client.delete(f"/api/ia/habilidades/curar/{curada_id}", headers=coord2).status_code, 403)

        db = self.Session()
        curada = db.get(HabilidadCurada, curada_id)
        self.assertEqual((curada.estado, curada.creado_por_correo), ("aprobada", "coord1@upb.edu.co"))
        db.close()

        self.assertEqual(self.curar(coord1, estado="descartada").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/ia/habilidades/curar/{curada_id}", headers=coord1).status_code, 200)

    def test_revertir_curaduria_la_retira_de_la_taxonomia(self):
        coord1 = self.login("coord1@upb.edu.co")
        texto = "En el cargo uso kubernetes_alcance a diario"
        creada = self.curar(coord1)
        self.assertIn("Kubernetes", extraer_habilidades_por_respuesta(texto))

        self.client.delete(f"/api/ia/habilidades/curar/{creada.json()['curada']['id']}", headers=coord1)
        self.assertNotIn("Kubernetes", extraer_habilidades_por_respuesta(texto))

    def test_otro_worker_alinea_la_taxonomia_con_la_base(self):
        # Simula un segundo proceso: la curaduría se borra en la BD sin pasar por esta memoria.
        coord1 = self.login("coord1@upb.edu.co")
        self.curar(coord1)
        db = self.Session()
        db.query(HabilidadCurada).delete()
        db.commit()
        sincronizar_curadurias_bd(db)
        db.close()
        self.assertNotIn("Kubernetes", extraer_habilidades_por_respuesta("uso kubernetes_alcance"))

    def test_exportacion_de_habilidades_genera_excel(self):
        db = self.Session()
        coord = db.query(Usuario).filter(Usuario.correo == "coord1@upb.edu.co").one()
        carga = Carga(nombre_archivo="m1.xlsx", hash_archivo="b" * 64, usuario_id=coord.id, sede_id=1, momento=1, anio_grado=2023, estado="vigente", version=1, registros=8)
        db.add(carga)
        db.flush()
        for i in range(8):
            documento = str(500000 + i)
            db.add(Egresado(numero_documento=documento, primer_nombre=f"Egresado{i}", programa="Derecho"))
            db.flush()
            # Dos mediciones anónimas y seis identificadas, con varias habilidades por respuesta.
            db.add(Medicion(
                carga_id=carga.id, egresado_documento=documento if i < 6 else None, momento=1, anio=2023, sede_id=1,
                respuestas={"Sugerencia para mejorar el programa": "Más Python, liderazgo y trabajo en equipo"},
            ))
        db.commit()
        db.close()
        respuesta = self.client.get("/api/ia/habilidades-export", headers=self.login("coord1@upb.edu.co"))
        self.assertEqual(respuesta.status_code, 200, respuesta.text[:300])
        self.assertEqual(respuesta.content[:2], b"PK")

    def test_prediccion_expone_la_estrategia_de_balanceo(self):
        # Trayectorias sintéticas M0 -> M1 (mínimo 30, ADR-019) para que el modelo entrene.
        db = self.Session()
        coord = db.query(Usuario).filter(Usuario.correo == "coord1@upb.edu.co").one()
        cargas = {}
        for momento in (0, 1):
            cargas[momento] = Carga(nombre_archivo=f"m{momento}.xlsx", hash_archivo=str(momento) * 64, usuario_id=coord.id,
                                    sede_id=1, momento=momento, anio_grado=2023, estado="vigente", version=1, registros=60)
            db.add(cargas[momento])
        db.flush()
        for i in range(60):
            documento = str(700000 + i)
            db.add(Egresado(numero_documento=documento, primer_nombre=f"E{i}", programa=("Derecho", "Medicina")[i % 2]))
            db.flush()
            db.add(Medicion(carga_id=cargas[0].id, egresado_documento=documento, momento=0, anio=2023, sede_id=1,
                            respuestas={"¿Aparte de estudiar, usted se dedica a trabajar?": "Sí" if i % 3 else "No",
                                        "En este trabajo usted es:": "Empleado de empresa particular"}))
            db.add(Medicion(carga_id=cargas[1].id, egresado_documento=documento, momento=1, anio=2023, sede_id=1,
                            respuestas={"¿Realiza alguna actividad remunerada?": "Sí" if i % 4 else "No",
                                        "La actividad remunerada que usted realiza actualmente es:": "Empleado de empresa particular",
                                        "Ingreso mensual en SMLV": "Entre 2 y 4 SMLV"}))
        db.commit()
        db.close()
        respuesta = self.client.get("/api/ia/prediccion-empleabilidad", headers=self.login("coord1@upb.edu.co"))
        self.assertEqual(respuesta.status_code, 200, respuesta.text[:300])
        self.assertEqual(respuesta.json()["estado"], "exitoso")
        # La interfaz muestra el badge de balanceo con este campo; el response_model no debe descartarlo.
        self.assertIn("Cost-Sensitive", respuesta.json().get("estrategia_balanceo") or "")

    def test_textos_libres_se_anonimizan_antes_del_analisis(self):
        respuestas = {"Sugerencia para la universidad": "Soy Laura Pérez, escriban a laura@mail.com o al 3001234567"}
        texto = " ".join(_extraer_textos_libres(respuestas, ["1098765432", "Laura", "Pérez"]))
        for dato in ("Laura", "Pérez", "laura@mail.com", "3001234567"):
            self.assertNotIn(dato, texto)


if __name__ == "__main__":
    unittest.main()
