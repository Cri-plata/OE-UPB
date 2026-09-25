import io
import unittest

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_current_user
from datetime import datetime

from domain.models import AuditoriaEgresado, Base, Carga, Egresado, EgresadoSede, EventoEliminacionCarga, Medicion, Sede, Usuario
from infrastructure.database import get_db
from main import app


class CargaTransaccionalTest(unittest.TestCase):
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
        db = self.Session()
        db.add(Sede(id=1, codigo="BUC", nombre="Bucaramanga"))
        db.add(
            Usuario(
                nombre="Coordinador de prueba",
                correo="coordinador@upb.edu.co",
                contrasena_hash="hash",
                rol="Coordinador_Sede",
                sede_id=1,
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
        app.dependency_overrides[get_current_user] = lambda: {
            "correo": "coordinador@upb.edu.co",
            "rol": "Coordinador_Sede",
            "sede_id": 1,
        }
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    @staticmethod
    def archivo_excel(nombre: str) -> tuple[str, bytes, str]:
        contenido = io.BytesIO()
        pd.DataFrame(
            [
                {
                    "NUMERO_DOCUMENTO": "CC-1",
                    "PRIMER NOMBRE": nombre,
                    "PRIMER_APELLIDO": "Prueba",
                    "PROGRAMA": "Ingeniería",
                    "FECHA_GRADO": "2024-06-01",
                }
            ]
        ).to_excel(contenido, index=False)
        return (
            "encuesta.xlsx",
            contenido.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_recarga_reemplaza_version_anterior_y_elimina_por_id(self):
        primera = self.client.post(
            "/api/carga/excel",
            data={"momento": "1", "anio": "2024"},
            files={"file": self.archivo_excel("Primera")},
        )
        segunda = self.client.post(
            "/api/carga/excel",
            data={"momento": "1", "anio": "2024"},
            files={"file": self.archivo_excel("Segunda")},
        )

        self.assertEqual(primera.status_code, 200, primera.text)
        self.assertEqual(segunda.status_code, 200, segunda.text)

        db = self.Session()
        cargas = db.query(Carga).order_by(Carga.version).all()
        self.assertEqual([c.estado for c in cargas], ["reemplazada", "vigente"])
        self.assertEqual([c.version for c in cargas], [1, 2])
        self.assertEqual(db.query(Medicion).count(), 1)
        self.assertEqual(db.query(Medicion).one().carga_id, cargas[1].id)
        carga_vigente_id = cargas[1].id
        db.close()

        historial = self.client.get("/api/carga/historial")
        self.assertEqual(historial.status_code, 200, historial.text)
        self.assertEqual(len(historial.json()), 2)

        eliminacion = self.client.request(
            "DELETE", f"/api/carga/archivo/{carga_vigente_id}",
            json={"motivo": "Carga duplicada confirmada en prueba"},
        )
        self.assertEqual(eliminacion.status_code, 200, eliminacion.text)

        db = self.Session()
        self.assertEqual(db.query(Medicion).count(), 0)
        self.assertIsNone(db.query(Carga).filter(Carga.id == carga_vigente_id).first())
        evento = db.query(EventoEliminacionCarga).filter(
            EventoEliminacionCarga.carga_id_eliminada == carga_vigente_id
        ).one()
        self.assertEqual(evento.motivo, "Carga duplicada confirmada en prueba")
        db.close()

        tercera = self.client.post(
            "/api/carga/excel",
            data={"momento": "1", "anio": "2024"},
            files={"file": self.archivo_excel("Tercera")},
        )
        self.assertEqual(tercera.status_code, 200, tercera.text)

        db = self.Session()
        ultima = db.query(Carga).order_by(Carga.version.desc()).first()
        self.assertEqual(ultima.version, 3)
        self.assertEqual(ultima.estado, "vigente")
        self.assertEqual(db.query(Medicion).count(), 1)
        db.close()


    def cargar(self, archivo, anio="2024"):
        return self.client.post("/api/carga/excel", data={"momento": "1", "anio": anio}, files={"file": archivo})

    def test_eliminar_carga_conserva_egresados_del_directorio_manual(self):
        db = self.Session()
        coordinador = db.query(Usuario).one()
        db.add(Egresado(numero_documento="MANUAL-1", primer_nombre="Manual", programa="Derecho"))
        db.flush()
        db.add(EgresadoSede(egresado_documento="MANUAL-1", sede_id=1, creado_por_id=coordinador.id))
        db.commit()
        db.close()

        carga = self.cargar(self.archivo_excel("Primera"))
        self.assertEqual(carga.status_code, 200, carga.text)
        eliminacion = self.client.request(
            "DELETE", f"/api/carga/archivo/{carga.json()['carga_id']}",
            json={"motivo": "Retiro de carga de prueba"},
        )
        self.assertEqual(eliminacion.status_code, 200, eliminacion.text)

        db = self.Session()
        self.assertIsNotNone(db.get(Egresado, "MANUAL-1"))
        self.assertIsNone(db.get(Egresado, "CC-1"))
        db.close()

    def test_archivo_identico_a_la_version_vigente_se_rechaza(self):
        archivo = self.archivo_excel("Primera")
        self.assertEqual(self.cargar(archivo).status_code, 200)
        repetida = self.cargar(archivo)
        self.assertEqual(repetida.status_code, 409, repetida.text)
        db = self.Session()
        self.assertEqual(db.query(Carga).count(), 1)
        db.close()

    def test_correccion_manual_prevalece_sobre_carga_posterior(self):
        db = self.Session()
        coordinador = db.query(Usuario).one()
        db.add(Egresado(numero_documento="CC-1", primer_nombre="Corregido", programa="Ingeniería", fecha_grado=datetime(2020, 1, 1)))
        db.add(AuditoriaEgresado(accion="editar", actor_id=coordinador.id, actor_correo=coordinador.correo, sede_id=1, egresado_documento="CC-1", cambios={}, motivo="Corrección manual"))
        db.commit()
        db.close()

        respuesta = self.cargar(self.archivo_excel("Original"))
        self.assertEqual(respuesta.status_code, 200, respuesta.text)
        self.assertIn("corrección manual", respuesta.json()["mensaje"])
        db = self.Session()
        egresado = db.get(Egresado, "CC-1")
        self.assertEqual(egresado.primer_nombre, "Corregido")
        self.assertEqual(egresado.fecha_grado, datetime(2020, 1, 1))
        db.close()

    def test_anio_fuera_de_rango_se_rechaza(self):
        respuesta = self.cargar(self.archivo_excel("Primera"), anio="1800")
        self.assertEqual(respuesta.status_code, 422, respuesta.text)

if __name__ == "__main__":
    unittest.main()
