"""
Pruebas unitarias para la normalización canónica y resolución difusa de programas académicos (IA-16).
"""

import unittest
from application.programas import (
    normalizar_forma_base,
    canonizar_programa,
    construir_mapa_canonico,
    _similitud_combinada,
)


class TestProgramaNormalizer(unittest.TestCase):

    def test_normalizacion_prefijos_y_sufijos(self):
        # Prefijos
        self.assertEqual(normalizar_forma_base("Pregrado en Ingeniería de Sistemas"), "INGENIERIA DE SISTEMAS")
        self.assertEqual(normalizar_forma_base("Programa de Administración de Empresas"), "ADMINISTRACION DE EMPRESAS")
        self.assertEqual(normalizar_forma_base("CARRERA DE DERECHO"), "DERECHO")

        # Sufijos de jornada y modalidad
        self.assertEqual(normalizar_forma_base("Ingeniería de Sistemas - Diurna"), "INGENIERIA DE SISTEMAS")
        self.assertEqual(normalizar_forma_base("Derecho (Nocturna)"), "DERECHO")
        self.assertEqual(normalizar_forma_base("Administración de Empresas (Virtual)"), "ADMINISTRACION DE EMPRESAS")
        self.assertEqual(normalizar_forma_base("Ingeniería Civil - Bucaramanga"), "INGENIERIA CIVIL")

    def test_expansion_abreviaturas(self):
        self.assertEqual(normalizar_forma_base("Ing. de Sistemas"), "INGENIERIA DE SISTEMAS")
        self.assertEqual(normalizar_forma_base("ING SISTEMAS"), "INGENIERIA SISTEMAS")
        self.assertEqual(normalizar_forma_base("Adm. de Negocios Int."), "ADMINISTRACION DE NEGOCIOS INTERNACIONALES")
        self.assertEqual(normalizar_forma_base("Lic. en Pedagogía"), "LICENCIATURA EN PEDAGOGIA")

    def test_canonizar_programa_sin_catalogo(self):
        # Sin catálogo oficial, devuelve formato Title Case respetuoso y acentuado
        resultado = canonizar_programa("ing. de sistemas - nocturna")
        self.assertEqual(resultado, "Ingeniería de Sistemas")

        resultado2 = canonizar_programa("PREGRADO EN DERECHO (BUCARAMANGA)")
        self.assertEqual(resultado2, "Derecho")

        # Homologación institucional de alias históricos y acentos (IA-16)
        self.assertEqual(
            canonizar_programa("Ingeniería Informática"),
            "Ingeniería de Sistemas e Informática",
        )
        self.assertEqual(
            canonizar_programa("Ingeniería de Sistemas e Informatica"),
            "Ingeniería de Sistemas e Informática",
        )
        self.assertEqual(
            canonizar_programa("Comunicación Social- Periodismo"),
            "Comunicación Social y Periodismo",
        )
        self.assertEqual(
            canonizar_programa("Ingeniería Mecanica"),
            "Ingeniería Mecánica",
        )
        self.assertEqual(
            canonizar_programa("Diseño Grafico"),
            "Diseño Gráfico",
        )

    def test_canonizar_programa_con_catalogo_fuzzy(self):
        catalogo = [
            "Ingeniería de Sistemas",
            "Administración de Negocios Internacionales",
            "Derecho",
            "Medicina",
        ]

        # Casos con ligeras variaciones que deben unificarse con el catálogo
        self.assertEqual(
            canonizar_programa("Ingenieria de Sistemas e Informatica", catalogo, umbral_similitud=0.75),
            "Ingeniería de Sistemas",
        )
        self.assertEqual(
            canonizar_programa("Ing. Sistemas", catalogo, umbral_similitud=0.80),
            "Ingeniería de Sistemas",
        )
        self.assertEqual(
            canonizar_programa("Adm. Negocios Internacionales", catalogo, umbral_similitud=0.80),
            "Administración de Negocios Internacionales",
        )
        self.assertEqual(
            canonizar_programa("DERECHO - NOCTURNA", catalogo),
            "Derecho",
        )

    def test_construir_mapa_canonico(self):
        observados = [
            "Ingeniería de Sistemas",
            "ING. DE SISTEMAS",
            "Ingeniería de Sistemas - Diurna",
            "Derecho",
            "Derecho (Nocturna)",
            "Medicina",
        ]

        mapa = construir_mapa_canonico(observados)
        self.assertEqual(mapa["Ingeniería de Sistemas"], "Ingeniería de Sistemas")
        self.assertEqual(mapa["ING. DE SISTEMAS"], "Ingeniería de Sistemas")
        self.assertEqual(mapa["Ingeniería de Sistemas - Diurna"], "Ingeniería de Sistemas")
        self.assertEqual(mapa["Derecho"], "Derecho")
        self.assertEqual(mapa["Derecho (Nocturna)"], "Derecho")
        self.assertEqual(mapa["Medicina"], "Medicina")


if __name__ == "__main__":
    unittest.main()
