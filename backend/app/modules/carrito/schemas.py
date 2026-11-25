"""Formatos de entrada y salida de la API del carrito."""
from datetime import datetime

from pydantic import BaseModel, Field


# ---------- Entrada ----------
class AgregarItem(BaseModel):
    producto_id: str = Field(min_length=1, max_length=64)
    cantidad: int = Field(default=1, ge=1, le=999)


class CambiarCantidad(BaseModel):
    cantidad: int = Field(ge=0, le=999, description="0 elimina el producto del carrito")


class ConfirmarPedido(BaseModel):
    # Total que el usuario vio en pantalla; si no coincide con el calculado por el
    # servidor, el pedido no se crea y se devuelve el resumen actualizado.
    total_esperado: float | None = None


# ---------- Salida ----------
class Beneficio(BaseModel):
    segmento: str
    porcentaje: float
    descripcion: str
    compra_minima: float
    aplicado: bool
    falta_para_aplicar: float


class LineaCarrito(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    importe: float
    stock: int | None
    imagen: str | None = None
    disponible: bool
    precio_cambiado: bool
    precio_actual: float | None


class Carrito(BaseModel):
    items: list[LineaCarrito]
    cantidad_articulos: int
    subtotal: float
    descuento: float
    total: float
    beneficio: Beneficio
    avisos: list[str] = []


class LineaPedido(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    importe: float


class Pedido(BaseModel):
    codigo: str
    estado: str
    creado: datetime
    segmento: str
    porcentaje_descuento: float
    subtotal: float
    descuento: float
    total: float
    items: list[LineaPedido]


class ResumenPedido(BaseModel):
    codigo: str
    estado: str
    creado: datetime
    total: float
    cantidad_articulos: int


class Confirmacion(BaseModel):
    mensaje: str
    pedido: Pedido
