"""Pruebas de punta a punta de la API del carrito (usa SQLite temporal).

Ejecutar desde backend/:  python -m unittest -v
Requiere: pip install -r requirements.txt httpx
"""
import json
import os
import tempfile
import unittest
from pathlib import Path

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
_productos = Path(_tmp) / "productos.json"
_productos.write_text(json.dumps([
    {"id": "P1", "nombre": "Taza", "precio": 10.00, "stock": 5},
    {"id": "P2", "nombre": "Lámpara", "precio": 25.50, "stock": 2},
    {"id": "P3", "nombre": "Agotado", "precio": 3.00, "stock": 0},
]), encoding="utf-8")
os.environ["PRODUCTOS_PATH"] = str(_productos)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402

with engine.begin() as c:
    # Tabla de prueba propia: "usuarios" ahora la crea el módulo de autenticación.
    c.execute(text("CREATE TABLE segmentos_prueba (id TEXT PRIMARY KEY, segmento TEXT)"))
    c.execute(text("INSERT INTO segmentos_prueba VALUES ('camp1', 'Campeones'), ('pro1', 'prometedores')"))

cliente = TestClient(app)


def h(usuario):
    return {"X-Usuario-Id": usuario}


def cambiar_precio(pid, precio):
    datos = json.loads(_productos.read_text(encoding="utf-8"))
    for p in datos:
        if p["id"] == pid:
            p["precio"] = precio
    _productos.write_text(json.dumps(datos), encoding="utf-8")
    st = _productos.stat()
    os.utime(_productos, (st.st_atime, st.st_mtime + 5))  # fuerza recarga del caché


class PruebasApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._previo = os.environ.get("SEGMENTO_SQL")
        os.environ["SEGMENTO_SQL"] = "SELECT segmento FROM segmentos_prueba WHERE id = :usuario_id"

    @classmethod
    def tearDownClass(cls):
        if cls._previo is None:
            os.environ.pop("SEGMENTO_SQL", None)
        else:
            os.environ["SEGMENTO_SQL"] = cls._previo

    def test_01_sin_usuario(self):
        self.assertEqual(cliente.get("/api/carrito").status_code, 422)

    def test_02_carrito_vacio_nuevo(self):
        r = cliente.get("/api/carrito", headers=h("anonimo")).json()
        self.assertEqual(r["items"], [])
        self.assertEqual(r["total"], 0)
        self.assertEqual(r["beneficio"]["segmento"], "Nuevo")

    def test_03_flujo_completo_campeones(self):
        u = h("camp1")
        r = cliente.post("/api/carrito/items", json={"producto_id": "P1", "cantidad": 2}, headers=u)
        self.assertEqual(r.status_code, 200, r.text)
        r = cliente.post("/api/carrito/items", json={"producto_id": "P2"}, headers=u).json()
        self.assertEqual(r["subtotal"], 45.50)
        self.assertEqual(r["beneficio"]["segmento"], "Campeones")
        self.assertEqual(r["descuento"], 2.28)  # 5% de 45.50 = 2.275
        self.assertEqual(r["total"], 43.22)

        r = cliente.put("/api/carrito/items/P1", json={"cantidad": 3}, headers=u).json()
        self.assertEqual(r["cantidad_articulos"], 4)

        r = cliente.post("/api/pedidos", json={"total_esperado": r["total"]}, headers=u)
        self.assertEqual(r.status_code, 201, r.text)
        conf = r.json()
        self.assertTrue(conf["pedido"]["codigo"].startswith("PED-"))
        self.assertEqual(conf["pedido"]["subtotal"], 55.50)
        self.assertEqual(conf["pedido"]["descuento"], 2.78)
        self.assertEqual(conf["pedido"]["total"], 52.72)

        self.assertEqual(cliente.get("/api/carrito", headers=u).json()["items"], [])
        hist = cliente.get("/api/pedidos", headers=u).json()
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0]["cantidad_articulos"], 4)
        det = cliente.get(f"/api/pedidos/{conf['pedido']['codigo']}", headers=u).json()
        self.assertEqual(len(det["items"]), 2)
        # otro usuario no puede ver el pedido
        self.assertEqual(cliente.get(f"/api/pedidos/{conf['pedido']['codigo']}", headers=h("x")).status_code, 404)

    def test_04_stock_y_productos(self):
        u = h("stock1")
        self.assertEqual(cliente.post("/api/carrito/items", json={"producto_id": "P3"}, headers=u).status_code, 409)
        self.assertEqual(cliente.post("/api/carrito/items", json={"producto_id": "NOEXISTE"}, headers=u).status_code, 404)
        self.assertEqual(cliente.post("/api/carrito/items", json={"producto_id": "P2", "cantidad": 3}, headers=u).status_code, 409)
        self.assertEqual(cliente.post("/api/carrito/items", json={"producto_id": "P1", "cantidad": 0}, headers=u).status_code, 422)

    def test_05_eliminar_y_vaciar(self):
        u = h("elim1")
        cliente.post("/api/carrito/items", json={"producto_id": "P1"}, headers=u)
        cliente.post("/api/carrito/items", json={"producto_id": "P2"}, headers=u)
        r = cliente.delete("/api/carrito/items/P1", headers=u).json()
        self.assertEqual([i["producto_id"] for i in r["items"]], ["P2"])
        r = cliente.put("/api/carrito/items/P2", json={"cantidad": 0}, headers=u).json()
        self.assertEqual(r["items"], [])
        cliente.post("/api/carrito/items", json={"producto_id": "P1"}, headers=u)
        self.assertEqual(cliente.delete("/api/carrito", headers=u).json()["items"], [])
        self.assertEqual(cliente.post("/api/pedidos", json={}, headers=u).status_code, 400)

    def test_06_compra_minima_segmento(self):
        u = h("pro1")  # "prometedores" -> Prometedores, 10% desde 50
        r = cliente.post("/api/carrito/items", json={"producto_id": "P1", "cantidad": 2}, headers=u).json()
        self.assertEqual(r["beneficio"]["segmento"], "Prometedores")
        self.assertFalse(r["beneficio"]["aplicado"])
        self.assertEqual(r["beneficio"]["falta_para_aplicar"], 30.0)
        r = cliente.put("/api/carrito/items/P1", json={"cantidad": 5}, headers=u).json()
        self.assertTrue(r["beneficio"]["aplicado"])
        self.assertEqual(r["descuento"], 5.0)

    def test_07_total_manipulado(self):
        u = h("trampa1")
        cliente.post("/api/carrito/items", json={"producto_id": "P1"}, headers=u)
        r = cliente.post("/api/pedidos", json={"total_esperado": 1.00}, headers=u)
        self.assertEqual(r.status_code, 409)
        self.assertIn("carrito", r.json()["detail"])

    def test_08_precio_cambia_antes_de_pagar(self):
        u = h("precio1")
        cliente.post("/api/carrito/items", json={"producto_id": "P1"}, headers=u)
        try:
            cambiar_precio("P1", 12.00)
            r = cliente.get("/api/carrito", headers=u).json()
            self.assertTrue(r["items"][0]["precio_cambiado"])
            r = cliente.post("/api/pedidos", json={}, headers=u)
            self.assertEqual(r.status_code, 409)
            r = cliente.post("/api/pedidos", json={}, headers=u)  # ya con precio actualizado
            self.assertEqual(r.status_code, 201, r.text)
            self.assertEqual(r.json()["pedido"]["subtotal"], 12.00)
        finally:
            cambiar_precio("P1", 10.00)


if __name__ == "__main__":
    unittest.main()
