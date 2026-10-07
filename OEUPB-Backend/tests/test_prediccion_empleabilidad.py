"""Pruebas del servicio y endpoint del modelo predictivo de empleabilidad (RF-71, ADR-019).

Usan SQLite en memoria y trayectorias sintéticas: nunca la base configurada en `.env`.
"""

import unittest

import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_password_hash
from application.prediccion_service import calcular_pesos_balanceados, predecir_empleabilidad_servicio
from domain.models import Base, Carga, Egresado, Medicion, Sede, Usuario
from infrastructure.database import get_db
from main import app

CLAVE = "ClaveSegura2026"


def poblar_trayectorias(db, coordinador_id: int, cantidad: int = 60) -> None:
    """Crea `cantidad` egresados con mediciones M0 y M1 de la cohorte 2023 en la sede 1."""
    cargas = {}
    for momento in (0, 1):
        cargas[momento] = Carga(
            nombre_archivo=f"m{momento}.xlsx", hash_archivo=str(momento) * 64, usuario_id=coordinador_id,
            sede_id=1, momento=momento, anio_grado=2023, estado="vigente", version=1, registros=cantidad,
        )
        db.add(cargas[momento])
    db.flush()
    for i in range(cantidad):
        documento = str(800000 + i)
        db.add(Egresado(numero_documento=documento, primer_nombre=f"E{i}", programa=("Derecho", "Medicina", "Psicología")[i % 3]))
        db.flush()
        db.add(Medicion(
            carga_id=cargas[0].id, egresado_documento=documento, momento=0, anio=2023, sede_id=1,
            respuestas={"¿Aparte de estudiar, usted se dedica a trabajar?": "Sí" if i % 3 else "No",
                        "En este trabajo usted es:": "Empleado de empresa particular"},
        ))
        db.add(Medicion(
            carga_id=cargas[1].id, egresado_documento=documento, momento=1, anio=2023, sede_id=1,
            respuestas={"¿Realiza alguna actividad remunerada?": "Sí" if i % 4 else "No",
                        "La actividad remunerada que usted realiza actualmente es:": ("Empleado de empresa particular", "Trabajador independiente")[i % 2],
                        "Ingreso mensual en SMLV": ("Entre 1 y 2 SMLV", "Entre 2 y 4 SMLV")[i % 2]},
        ))
    db.commit()


class PrediccionEmpleabilidadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        db = self.Session()
        db.add(Sede(id=1, codigo="BUC", nombre="Bucaramanga"))
        coordinador = Usuario(nombre="Coord", correo="coord@upb.edu.co", contrasena_hash=get_password_hash(CLAVE), rol="Coordinador_Sede", sede_id=1)
        db.add(coordinador)
        db.commit()
        poblar_trayectorias(db, coordinador.id)
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

    def predecir(self, momento_destino: int) -> dict:
        db = self.Session()
        try:
            return predecir_empleabilidad_servicio(
                mediciones=db.query(Medicion).all(), egresados=db.query(Egresado).all(),
                momento_origen=0, momento_destino=momento_destino,
            )
        finally:
            db.close()

    def test_servicio_entrena_y_reporta_robustez(self):
        resultado = self.predecir(1)
        self.assertEqual(resultado["estado"], "exitoso")
        self.assertGreaterEqual(resultado["total_trayectorias"], 30)
        self.assertGreater(resultado["precision_modelo"], 0)
        self.assertGreaterEqual(resultado["f1_score"], 0)
        self.assertTrue(resultado["predicciones_programas"])
        self.assertTrue(resultado["importancia_factores"])
        self.assertIn("clases", resultado["matriz_confusion"])
        robustez = resultado["indicadores_robustez"]
        self.assertIn(robustez["nivel_general"], ("Alta", "Media", "Baja"))
        self.assertIn(robustez["color_general"], ("verde", "amarillo", "rojo"))
        for clave in ("muestra", "balance_clases", "precision"):
            self.assertIn(clave, robustez)
        self.assertTrue(robustez["observaciones"])
        self.assertIn("disponible", resultado["validacion_temporal"])

    def test_servicio_informa_datos_insuficientes(self):
        # No hay mediciones M5: el horizonte de 5 años no alcanza las 30 trayectorias.
        resultado = self.predecir(5)
        self.assertEqual(resultado["estado"], "insuficiente_datos")
        self.assertLess(resultado["total_trayectorias"], 30)
        self.assertIn("mínimo de 30", resultado["mensaje"])

    def test_endpoint_responde_con_esquema_completo(self):
        token = self.client.post("/api/auth/login", json={"correoInstitucional": "coord@upb.edu.co", "contrasena": CLAVE}).json()["token"]
        respuesta = self.client.get(
            "/api/ia/prediccion-empleabilidad", params={"momento_origen": 0, "momento_destino": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.text[:300])
        datos = respuesta.json()
        self.assertEqual(datos["estado"], "exitoso")
        for clave in ("total_trayectorias", "precision_modelo", "predicciones_programas", "validacion_temporal"):
            self.assertIn(clave, datos)
        self.assertIn("Cost-Sensitive", datos.get("estrategia_balanceo") or "")

    def test_pesos_compensan_el_desbalance_de_clases(self):
        y = np.array(["A"] * 80 + ["B"] * 15 + ["C"] * 5)
        pesos = calcular_pesos_balanceados(y, factor_suavizado=0.65)
        self.assertEqual(len(pesos), len(y))
        self.assertAlmostEqual(float(np.mean(pesos)), 1.0, places=5)
        self.assertGreater(pesos[y == "C"][0], pesos[y == "B"][0])
        self.assertGreater(pesos[y == "B"][0], pesos[y == "A"][0])

    def test_servicio_declara_la_estrategia_de_balanceo(self):
        resultado = self.predecir(1)
        self.assertIn("Cost-Sensitive", resultado["estrategia_balanceo"])
        self.assertIn("Cost-Sensitive", resultado["indicadores_robustez"]["estrategia_balanceo"])


if __name__ == "__main__":
    unittest.main()
