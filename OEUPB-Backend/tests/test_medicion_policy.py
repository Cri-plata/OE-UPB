import unittest
from types import SimpleNamespace

from application.medicion_policy import POLITICAS_INDICADORES, seleccionar_intentos


class MedicionPolicyTest(unittest.TestCase):
    def medicion(self, id_, documento, intento):
        return SimpleNamespace(
            id=id_, egresado_documento=documento, sede_id=1,
            momento=1, anio=2025, intento=intento,
        )

    def test_indicadores_declaran_regla(self):
        self.assertEqual(
            set(POLITICAS_INDICADORES),
            {"reporte_general", "tendencias", "explorador"},
        )

    def test_selecciona_ultimo_intento_e_incluye_anonimos(self):
        primero = self.medicion(1, "123", 1)
        ultimo = self.medicion(2, "123", 2)
        anonimo_a = self.medicion(3, None, 1)
        anonimo_b = self.medicion(4, None, 1)
        resultado = seleccionar_intentos([primero, ultimo, anonimo_a, anonimo_b])
        self.assertEqual({item.id for item in resultado}, {2, 3, 4})


if __name__ == "__main__":
    unittest.main()
