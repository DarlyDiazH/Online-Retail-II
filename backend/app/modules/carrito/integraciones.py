"""Puntos de conexión con los otros módulos.

- Productos (Persona 2): se leen del JSON/CSV del catálogo (PRODUCTOS_PATH).
  Mientras ese archivo no exista se usan los productos de ejemplo de este módulo.
- Segmento del usuario (Persona 1): se consulta en Neon con SEGMENTO_SQL.
  Si no hay coincidencia o la tabla aún no existe, se usa "Nuevo".

Cuando los otros módulos tengan sus propias funciones (p. ej.
app.modules.catalogo.service.obtener_producto), basta con cambiar estas dos
funciones para que las llamen; el resto del carrito no cambia.
"""
import csv
import json
import logging
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from .descuentos import resolver_segmento

log = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parents[3]
_EJEMPLO = Path(__file__).with_name("productos_ejemplo.json")
# Archivo del módulo de catálogo (Persona 2): fuente oficial de productos.
_CATALOGO = _BACKEND_DIR / "app" / "modules" / "catalogo" / "data" / "productos.json"

# Nombres de columna aceptados (el catálogo puede usar español o inglés)
_CAMPOS = {
    "id": ("id", "producto_id", "StockCode", "stock_code", "codigo"),
    "nombre": ("nombre", "Description", "descripcion", "name"),
    "precio": ("precio", "Price", "price", "UnitPrice"),
    "stock": ("stock", "existencias", "Quantity", "cantidad"),
    "categoria": ("categoria", "category", "Categoria"),
    "imagen": ("imagen", "image", "imagen_url", "url_imagen"),
}


def _tomar(fila: dict, campo: str):
    for clave in _CAMPOS[campo]:
        if clave in fila and fila[clave] not in (None, ""):
            return fila[clave]
    return None


def _normalizar_producto(fila: dict) -> dict | None:
    pid, precio = _tomar(fila, "id"), _tomar(fila, "precio")
    if pid is None or precio is None:
        return None
    try:
        precio = Decimal(str(precio))
    except InvalidOperation:
        return None
    stock = _tomar(fila, "stock")
    try:
        stock = int(float(stock)) if stock is not None else None
    except ValueError:
        stock = None
    if fila.get("disponible") is False:  # el catálogo puede marcar un producto como no disponible
        stock = 0
    return {
        "id": str(pid),
        "nombre": str(_tomar(fila, "nombre") or pid),
        "precio": precio,
        "stock": stock,  # None = sin control de inventario
        "categoria": _tomar(fila, "categoria"),
        "imagen": _tomar(fila, "imagen"),
    }


def _ruta_catalogo() -> Path:
    """PRODUCTOS_PATH si está definido; si no, el productos.json del módulo de catálogo;
    y si tampoco existe, los productos de ejemplo del carrito."""
    valor = os.getenv("PRODUCTOS_PATH")
    if valor:
        ruta = Path(valor)
        ruta = ruta if ruta.is_absolute() else _BACKEND_DIR / ruta
        if ruta.exists():
            return ruta
        log.warning("PRODUCTOS_PATH=%s no existe; se usa el catálogo por defecto", valor)
    return _CATALOGO if _CATALOGO.exists() else _EJEMPLO


_cache: dict = {"mtime": None, "ruta": None, "productos": {}}


def _cargar_productos() -> dict[str, dict]:
    ruta = _ruta_catalogo()
    mtime = ruta.stat().st_mtime
    if _cache["ruta"] == ruta and _cache["mtime"] == mtime:
        return _cache["productos"]

    if ruta.suffix.lower() == ".csv":
        with ruta.open(encoding="utf-8-sig", newline="") as f:
            filas = list(csv.DictReader(f))
    else:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        filas = datos.get("productos", datos) if isinstance(datos, dict) else datos

    productos = {}
    for fila in filas:
        p = _normalizar_producto(fila)
        if p:
            productos[p["id"]] = p
    _cache.update(ruta=ruta, mtime=mtime, productos=productos)
    return productos


def obtener_producto(producto_id: str) -> dict | None:
    """Precio y disponibilidad actuales de un producto según el catálogo."""
    return _cargar_productos().get(str(producto_id))


def obtener_segmento(db: Session, usuario_id: str) -> str:
    """Segmento del usuario en Neon; 'Nuevo' si no existe coincidencia."""
    consulta = os.getenv("SEGMENTO_SQL") or (
        "SELECT v.segmento FROM usuarios u "
        "JOIN vw_descuentos_checkout v ON v.customer_id = u.customer_id "
        "WHERE u.id = :usuario_id"
    )
    try:
        valor = db.execute(text(consulta), {"usuario_id": usuario_id}).scalar()
    except Exception as e:  # tabla aún no creada, columna distinta, etc.
        log.warning("No se pudo consultar el segmento (%s); se usa 'Nuevo'", e)
        db.rollback()
        valor = None
    return resolver_segmento(valor)
