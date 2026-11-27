"""Pruebas del módulo de autenticación (usa SQLite temporal).

Ejecutar desde backend/:  python -m unittest -v
"""
import os
import tempfile
import unittest

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test_auth.db"
SEGMENTO_SQL = (
    "SELECT c.segmento FROM usuarios u JOIN clientes c ON c.customer_id = u.customer_id "
    "WHERE u.id = :usuario_id"
)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402

with engine.begin() as c:
    c.execute(text("CREATE TABLE clientes (customer_id INTEGER PRIMARY KEY, segmento TEXT)"))
    c.execute(text("INSERT INTO clientes VALUES (17850, 'Campeones')"))

http = TestClient(app)
REG = {"nombre": "Ana Pérez", "correo": "ana@correo.com", "contrasena": "clave1234"}


class PruebasAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._previo = os.environ.get("SEGMENTO_SQL")
        os.environ["SEGMENTO_SQL"] = SEGMENTO_SQL
        cls._previo_cliente = os.environ.get("CLIENTE_SQL")
        os.environ["CLIENTE_SQL"] = "SELECT 1 FROM clientes WHERE customer_id = :customer_id"

    @classmethod
    def tearDownClass(cls):
        if cls._previo_cliente is None:
            os.environ.pop("CLIENTE_SQL", None)
        else:
            os.environ["CLIENTE_SQL"] = cls._previo_cliente
        if cls._previo is None:
            os.environ.pop("SEGMENTO_SQL", None)
        else:
            os.environ["SEGMENTO_SQL"] = cls._previo

    def test_01_registro_nuevo(self):
        r = http.post("/api/auth/registro", json=REG)
        self.assertEqual(r.status_code, 201)
        d = r.json()
        self.assertEqual(d["segmento"], "Nuevo")
        self.assertTrue(d["es_nuevo"])
        self.assertIsNone(d["customer_id"])

    def test_02_correo_repetido(self):
        self.assertEqual(http.post("/api/auth/registro", json=REG).status_code, 409)

    def test_03_contrasena_corta(self):
        r = http.post("/api/auth/registro", json={**REG, "correo": "b@correo.com", "contrasena": "123"})
        self.assertEqual(r.status_code, 422)

    def test_04_login_ok_y_fallido(self):
        ok = http.post("/api/auth/login", json={"correo": "ANA@correo.com", "contrasena": "clave1234"})
        self.assertEqual(ok.status_code, 200)
        mal = http.post("/api/auth/login", json={"correo": "ana@correo.com", "contrasena": "otra"})
        self.assertEqual(mal.status_code, 401)

    def test_05_vincula_cliente_historico(self):
        r = http.post("/api/auth/registro",
                      json={**REG, "correo": "vip@correo.com", "customer_id": 17850})
        self.assertEqual(r.status_code, 201)
        d = r.json()
        self.assertEqual(d["segmento"], "Campeones")
        self.assertFalse(d["es_nuevo"])
        self.assertEqual(d["beneficio"]["porcentaje"], 5)

    def test_06_customer_id_inexistente_o_repetido(self):
        r = http.post("/api/auth/registro", json={**REG, "correo": "x@correo.com", "customer_id": 99999})
        self.assertEqual(r.status_code, 400)
        r = http.post("/api/auth/registro", json={**REG, "correo": "y@correo.com", "customer_id": 17850})
        self.assertEqual(r.status_code, 409)

    def test_07_perfil(self):
        uid = http.post("/api/auth/login", json={"correo": "ana@correo.com", "contrasena": "clave1234"}).json()["id"]
        r = http.get("/api/auth/perfil", headers={"X-Usuario-Id": str(uid)})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["correo"], "ana@correo.com")
        self.assertEqual(http.get("/api/auth/perfil", headers={"X-Usuario-Id": "abc"}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
