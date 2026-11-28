import json
from pathlib import Path
from typing import Optional

from .schemas import Producto


DATA_PATH = Path(__file__).resolve().parent / "data" / "productos.json"


def cargar_productos() -> list[Producto]:
    with DATA_PATH.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return [Producto(**item) for item in datos]


def obtener_productos(
    busqueda: Optional[str] = None,
    categoria: Optional[str] = None,
    solo_disponibles: bool = False,
) -> list[Producto]:
    productos = cargar_productos()

    if busqueda:
        termino = busqueda.strip().lower()
        productos = [
            p
            for p in productos
            if termino in p.nombre.lower()
            or termino in p.descripcion.lower()
            or termino in p.stock_code.lower()
        ]

    if categoria and categoria.strip().lower() != "todas":
        cat_objetivo = categoria.strip().lower()
        productos = [p for p in productos if p.categoria.strip().lower() == cat_objetivo]

    if solo_disponibles:
        productos = [p for p in productos if p.disponible and p.stock > 0]

    return productos


def obtener_producto_por_id(producto_id: str) -> Optional[Producto]:
    productos = cargar_productos()
    for producto in productos:
        if producto.id.lower() == producto_id.strip().lower():
            return producto
    return None


def listar_categorias() -> list[str]:
    productos = cargar_productos()
    categorias = sorted({p.categoria for p in productos})
    return categorias


def consultar_disponibilidad(producto_id: str, cantidad: int = 1) -> Optional[dict]:
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return None

    hay_stock = producto.disponible and producto.stock >= cantidad and cantidad > 0
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "stock_disponible": producto.stock,
        "cantidad_solicitada": cantidad,
        "disponible_para_cantidad": hay_stock,
    }