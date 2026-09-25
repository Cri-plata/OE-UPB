import unittest

from application.indicadores import ETIQUETA_OTROS, UMBRAL_MINIMO_PUBLICACION, _agrupar_categorias, es_variable_analitica
from main import ruta_para_log


class CatalogoVariablesTest(unittest.TestCase):
    def test_excluye_familias_personales_y_administrativas(self):
        # Campos reportados en H-EXP-01 y alias frecuentes.
        prohibidas = [
            "NUMERO_DOCUMENTO", "Número de documento", "Cédula", "PRIMER NOMBRE", "PRIMER_APELLIDO",
            "Segundo apellido", "CORREO", "Email", "Email opcional", "E-mail", "Celular", "Teléfono",
            "Fecha de nacimiento", "FECHA_GRADO", "Fecha de respuesta", "ID de respuesta", "ID",
            "Código de estado", "Código de encuesta", "Código IES", "IES", "Estado de encuesta",
            "Nivel académico", "Nivel de formación", "País",
        ]
        for columna in prohibidas:
            with self.subTest(columna=columna):
                self.assertFalse(es_variable_analitica(columna))

    def test_conserva_preguntas_analiticas(self):
        permitidas = [
            "¿Realiza alguna actividad remunerada?",
            "Califique su nivel de satisfacción con la estabilidad",
            "PROGRAMA",
            "Sector económico de la empresa",
        ]
        for columna in permitidas:
            with self.subTest(columna=columna):
                self.assertTrue(es_variable_analitica(columna))


class SupresionCeldasTest(unittest.TestCase):
    def test_agrupa_o_suprime_categorias_bajo_el_umbral(self):
        k = UMBRAL_MINIMO_PUBLICACION
        self.assertEqual(_agrupar_categorias({"A": k, "B": 1}), (["A"], [float(k)]))
        self.assertEqual(
            _agrupar_categorias({"A": k + 1, "B": k - 1, "C": k - 1}),
            (["A", ETIQUETA_OTROS], [float(k + 1), float(2 * (k - 1))]),
        )


class LogSinDocumentosTest(unittest.TestCase):
    def test_oculta_documento_en_rutas_del_directorio(self):
        self.assertEqual(ruta_para_log("/api/directorio/perfil/1098765432"), "/api/directorio/perfil/{documento}")
        self.assertEqual(ruta_para_log("/api/directorio/egresados/CC-1"), "/api/directorio/egresados/{documento}")
        self.assertEqual(ruta_para_log("/api/usuarios/3"), "/api/usuarios/3")


if __name__ == "__main__":
    unittest.main()
