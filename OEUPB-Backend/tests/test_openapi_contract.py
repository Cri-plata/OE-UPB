import json
import unittest
from pathlib import Path

from main import app


class OpenApiContractTest(unittest.TestCase):
    def test_openapi_versionado_y_respuestas_tipadas(self):
        contract = app.openapi()
        for path, operations in contract["paths"].items():
            if path != "/":
                self.assertTrue(path.startswith("/api/"), path)
                self.assertFalse(path.startswith("/api/v1/"), path)
            for method, operation in operations.items():
                if method not in {"get", "post", "put", "patch", "delete"} or path == "/":
                    continue
                codigo_exito = next(
                    (codigo for codigo in operation["responses"] if codigo.startswith("2")),
                    None,
                )
                self.assertIsNotNone(codigo_exito, f"{method.upper()} {path} no declara éxito")
                contenidos = operation["responses"][codigo_exito].get("content", {})
                schema = next((contenido.get("schema") for contenido in contenidos.values() if contenido.get("schema")), None)
                self.assertTrue(schema, f"{method.upper()} {path} no tiene respuesta tipada")

    def test_archivo_canonico_coincide_con_fastapi(self):
        root = Path(__file__).resolve().parents[2]
        saved = json.loads((root / "OEUPB-Docs" / "specs" / "api" / "openapi.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, app.openapi())


if __name__ == "__main__":
    unittest.main()
