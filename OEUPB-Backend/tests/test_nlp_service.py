import unittest
from application.nlp_service import anonimizar, clasificar


class NlpServiceTest(unittest.TestCase):
    def test_anonimiza_y_clasifica_sin_exponer_pii(self):
        texto = anonimizar("Carlos Ruiz 300 555 9988 carlos@example.com necesita liderazgo y trabajo en equipo; está sin empleo", ["Carlos", "Ruiz"])
        self.assertNotIn("Carlos", texto)
        self.assertNotIn("example.com", texto)
        conteo, negativos = clasificar([texto])
        self.assertEqual(conteo["Liderazgo"], 1)
        self.assertEqual(conteo["Trabajo en equipo"], 1)
        self.assertEqual(negativos, 1)


if __name__ == "__main__": unittest.main()
