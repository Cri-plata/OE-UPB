import unittest

from fastapi import HTTPException

from presentation.carga_router import (
    validar_coordinador_con_sede,
    validar_momento,
)


class ValidacionesCargaTest(unittest.TestCase):
    def test_acepta_momentos_permitidos(self):
        for momento in (0, 1, 5):
            validar_momento(momento)

    def test_rechaza_momento_no_permitido(self):
        with self.assertRaises(HTTPException) as error:
            validar_momento(2)

        self.assertEqual(error.exception.status_code, 422)

    def test_acepta_coordinador_con_sede(self):
        sede_id = validar_coordinador_con_sede(
            {"rol": "Coordinador_Sede", "sede_id": 2}
        )

        self.assertEqual(sede_id, 2)

    def test_rechaza_otro_rol(self):
        with self.assertRaises(HTTPException) as error:
            validar_coordinador_con_sede({"rol": "Admin_CTIC", "sede_id": None})

        self.assertEqual(error.exception.status_code, 403)

    def test_rechaza_coordinador_sin_sede(self):
        with self.assertRaises(HTTPException) as error:
            validar_coordinador_con_sede(
                {"rol": "Coordinador_Sede", "sede_id": None}
            )

        self.assertEqual(error.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
