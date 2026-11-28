from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_listar_productos():
    response = client.get("/catalogo/productos")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6
    assert len(data["productos"]) == 6


def test_filtrar_por_categoria():
    response = client.get("/catalogo/productos", params={"categoria": "Cocina"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(p["categoria"] == "Cocina" for p in data["productos"])


def test_buscar_producto():
    response = client.get("/catalogo/productos", params={"busqueda": "lámpara"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["productos"][0]["id"] == "PROD-001"


def test_solo_disponibles():
    response = client.get("/catalogo/productos", params={"solo_disponibles": True})
    assert response.status_code == 200
    data = response.json()
    assert all(p["disponible"] and p["stock"] > 0 for p in data["productos"])


def test_detalle_y_disponibilidad():
    detalle = client.get("/catalogo/productos/PROD-001")
    assert detalle.status_code == 200
    assert detalle.json()["stock_code"] == "85123A"

    disp = client.get("/catalogo/productos/PROD-005/disponibilidad", params={"cantidad": 1})
    assert disp.status_code == 200
    assert disp.json()["disponible_para_cantidad"] is False