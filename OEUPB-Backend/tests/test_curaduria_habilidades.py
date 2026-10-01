"""
Pruebas de la API de Curaduría de Habilidades Emergentes (IA-15 / Human-in-the-Loop).
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from infrastructure.database import SessionLocal, Base, engine
from domain.models import Usuario, HabilidadCurada
from application.auth_service import create_access_token
from application.ia_service import (
    extraer_habilidades_por_respuesta,
    _extraer_emergentes_tfidf,
    invalidar_cache_taxonomia,
    sincronizar_curadurias_bd,
)


class TestCuraduriaHabilidades(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        db = SessionLocal()
        try:
            # Buscar o crear usuario de prueba Coordinador
            user_coord = db.query(Usuario).filter(Usuario.correo == "coord_curador@upb.edu.co").first()
            if not user_coord:
                user_coord = Usuario(
                    nombre="Coordinador Curador",
                    correo="coord_curador@upb.edu.co",
                    contrasena_hash="fakehash",
                    rol="Coordinador_Sede",
                    sede_id=1,
                    activo=True,
                    version_autorizacion=1,
                )
                db.add(user_coord)
                db.commit()
                db.refresh(user_coord)
            cls.coord_token = create_access_token({
                "sub": user_coord.correo,
                "usuario_id": user_coord.id,
                "rol": user_coord.rol,
                "sede_id": user_coord.sede_id,
                "version_autorizacion": user_coord.version_autorizacion,
            })
            cls.coord_id = user_coord.id

            # Limpiar curadurías de prueba previas
            db.query(HabilidadCurada).filter(
                HabilidadCurada.termino_original.in_(["docker_test", "ruido_test"])
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()

    def tearDown(self):
        db = SessionLocal()
        try:
            db.query(HabilidadCurada).filter(
                HabilidadCurada.termino_original.in_(["docker_test", "ruido_test"])
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()
        invalidar_cache_taxonomia()

    def test_aprobar_habilidad_emergente(self):
        # 1. Enviar solicitud de aprobación por Coordinador_Sede
        response = self.client.post(
            "/api/ia/habilidades/curar",
            json={
                "termino_original": "docker_test",
                "etiqueta_canonica": "Docker y Contenedores Test",
                "tipo": "dura",
                "variantes": ["docker_test", "contenedores docker_test"],
                "estado": "aprobada",
            },
            headers={"Authorization": f"Bearer {self.coord_token}"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("curada", data)
        self.assertEqual(data["curada"]["estado"], "aprobada")
        self.assertEqual(data["curada"]["etiqueta_canonica"], "Docker y Contenedores Test")

        # 2. Verificar que el motor de IA ahora la detecta en un texto
        texto_prueba = "El trabajo exige manejo de docker_test para despliegues"
        habs_detectadas = extraer_habilidades_por_respuesta(texto_prueba)
        self.assertIn("Docker y Contenedores Test", habs_detectadas)

    def test_descartar_termino_ruido(self):
        # 1. Descartar un término de ruido
        response = self.client.post(
            "/api/ia/habilidades/curar",
            json={
                "termino_original": "ruido_test",
                "etiqueta_canonica": "Ruido",
                "tipo": "dura",
                "variantes": ["ruido_test"],
                "estado": "descartada",
            },
            headers={"Authorization": f"Bearer {self.coord_token}"},
        )
        self.assertEqual(response.status_code, 200, response.text)

        # 2. Verificar que TF-IDF lo excluye
        textos = ["este es un texto con ruido_test y conceptos varios"]
        emergentes = _extraer_emergentes_tfidf(textos, top_n=10)
        terminos = [e["termino"] for e in emergentes]
        self.assertNotIn("ruido_test", terminos)

    def test_listar_y_eliminar_curaduria(self):
        # Crear curaduría
        post_resp = self.client.post(
            "/api/ia/habilidades/curar",
            json={
                "termino_original": "docker_test",
                "etiqueta_canonica": "Docker Test",
                "tipo": "dura",
                "variantes": ["docker_test"],
                "estado": "aprobada",
            },
            headers={"Authorization": f"Bearer {self.coord_token}"},
        )
        curada_id = post_resp.json()["curada"]["id"]

        # Listar
        list_resp = self.client.get(
            "/api/ia/habilidades/curadas",
            headers={"Authorization": f"Bearer {self.coord_token}"},
        )
        self.assertEqual(list_resp.status_code, 200)
        items = list_resp.json()
        self.assertTrue(any(i["id"] == curada_id for i in items))

        # Eliminar
        del_resp = self.client.delete(
            f"/api/ia/habilidades/curar/{curada_id}",
            headers={"Authorization": f"Bearer {self.coord_token}"},
        )
        self.assertEqual(del_resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
