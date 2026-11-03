import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import MagicMock, patch


RUTA = Path(__file__).resolve().parents[1] / "api-pelicula" / "CrearPelicula.py"
SPEC = importlib.util.spec_from_file_location("CrearPelicula", RUTA)
MODULO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULO)
EJEMPLOS = Path(__file__).resolve().parents[1] / "ejemplos"


class CrearPeliculaTests(TestCase):
    def setUp(self):
        self.contexto = SimpleNamespace(aws_request_id="request-de-prueba")

    def _invocar(self, evento, recurso=None):
        salida = io.StringIO()
        if recurso is None:
            recurso = MagicMock()
        with patch.object(MODULO.boto3, "resource", return_value=recurso), patch.dict(
            os.environ, {"TABLE_NAME": "dev-t_peliculas"}
        ), contextlib.redirect_stdout(salida):
            respuesta = MODULO.lambda_handler(evento, self.contexto)
        registros = [json.loads(linea) for linea in salida.getvalue().splitlines()]
        return respuesta, registros, recurso

    def test_crea_pelicula_y_registra_info_json(self):
        cuerpo = (EJEMPLOS / "pelicula_01.json").read_text(encoding="utf-8")
        respuesta, registros, recurso = self._invocar({"body": cuerpo})
        self.assertEqual(respuesta["statusCode"], 201)
        pelicula = json.loads(respuesta["body"])["pelicula"]
        self.assertEqual(pelicula["tenant_id"], "CINEPLANET")
        self.assertEqual(registros[0]["tipo"], "INFO")
        self.assertEqual(registros[0]["log_datos"]["uuid"], pelicula["uuid"])
        recurso.Table.assert_called_once_with("dev-t_peliculas")
        recurso.Table.return_value.put_item.assert_called_once_with(Item=pelicula)

    def test_muestra_con_error_registra_error_y_responde_400(self):
        cuerpo = (EJEMPLOS / "pelicula_07_error.json").read_text(encoding="utf-8")
        respuesta, registros, recurso = self._invocar({"body": cuerpo})
        self.assertEqual(respuesta["statusCode"], 400)
        self.assertEqual(registros[0]["tipo"], "ERROR")
        self.assertIn("pelicula_datos", registros[0]["log_datos"]["error"])
        recurso.Table.assert_not_called()

    def test_fallo_dynamodb_registra_error_y_responde_500(self):
        cuerpo = (EJEMPLOS / "pelicula_01.json").read_text(encoding="utf-8")
        recurso = MagicMock()
        recurso.Table.return_value.put_item.side_effect = RuntimeError("fallo simulado")
        respuesta, registros, _ = self._invocar({"body": cuerpo}, recurso)
        self.assertEqual(respuesta["statusCode"], 500)
        self.assertEqual(registros[0]["tipo"], "ERROR")
        self.assertEqual(registros[0]["log_datos"]["error_tipo"], "RuntimeError")
        self.assertNotIn("fallo simulado", respuesta["body"])


if __name__ == "__main__":
    main()
