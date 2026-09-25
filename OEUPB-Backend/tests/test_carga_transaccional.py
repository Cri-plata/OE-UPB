import io
import unittest

import pandas as pd
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from application.auth_service import get_current_user
from domain.models import Base, Carga, EventoEliminacionCarga, Medicion, Sede, Usuario
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


if __name__ == "__main__":
    unittest.main()
