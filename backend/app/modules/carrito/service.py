"""Lógica del carrito y del proceso de compra."""
import secrets
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import integraciones
from .calculos import Linea, calcular_totales, redondear
from .models import Carrito, CarritoItem, Pedido, PedidoItem


class ErrorCarrito(Exception):
    def __init__(self, estado: int, mensaje: str, detalle: dict | None = None):
        super().__init__(mensaje)
        self.estado = estado
        self.mensaje = mensaje
        self.detalle = detalle or {}


def _dec(valor) -> Decimal:
    return redondear(Decimal(str(valor)))


# ---------------------------------------------------------------- carrito
def _carrito(db: Session, usuario_id: str) -> Carrito:
    carrito = db.scalar(select(Carrito).where(Carrito.usuario_id == usuario_id))
    if carrito is None:
        carrito = Carrito(usuario_id=usuario_id)
        db.add(carrito)
        db.flush()
    return carrito


def _item(carrito: Carrito, producto_id: str) -> CarritoItem | None:
    return next((i for i in carrito.items if i.producto_id == producto_id), None)


def _producto_o_error(producto_id: str) -> dict:
    producto = integraciones.obtener_producto(producto_id)
    if producto is None:
        raise ErrorCarrito(404, f"El producto {producto_id} no existe en el catálogo.")
    return producto


def _validar_stock(producto: dict, cantidad: int):
    stock = producto["stock"]
    if stock is not None and cantidad > stock:
        if stock <= 0:
            raise ErrorCarrito(409, f"'{producto['nombre']}' está agotado.")
        raise ErrorCarrito(
            409,
            f"Solo hay {stock} unidades disponibles de '{producto['nombre']}'.",
            {"producto_id": producto["id"], "stock": stock},
        )


def ver_carrito(db: Session, usuario_id: str) -> dict:
    carrito = _carrito(db, usuario_id)
    db.commit()
    segmento = integraciones.obtener_segmento(db, usuario_id)

    lineas, items, avisos = [], [], []
    for it in carrito.items:
        producto = integraciones.obtener_producto(it.producto_id)
        precio = _dec(it.precio_unitario)
        precio_actual = producto["precio"] if producto else None
        stock = producto["stock"] if producto else 0
        disponible = producto is not None and (stock is None or it.cantidad <= stock)
        cambiado = precio_actual is not None and _dec(precio_actual) != precio

        if not producto:
            avisos.append(f"'{it.nombre}' ya no está en el catálogo.")
        elif not disponible:
            avisos.append(f"'{it.nombre}': solo quedan {stock} unidades.")
        if cambiado:
            avisos.append(f"El precio de '{it.nombre}' cambió de {precio} a {_dec(precio_actual)}.")

        linea = Linea(it.producto_id, it.nombre, precio, it.cantidad)
        lineas.append(linea)
        items.append({
            "producto_id": it.producto_id,
            "nombre": it.nombre,
            "precio_unitario": float(precio),
            "cantidad": it.cantidad,
            "importe": float(linea.importe),
            "stock": stock,
            "imagen": producto.get("imagen") if producto else None,
            "disponible": disponible,
            "precio_cambiado": cambiado,
            "precio_actual": float(precio_actual) if precio_actual is not None else None,
        })

    totales = calcular_totales(lineas, segmento)
    return {"items": items, "avisos": avisos, **_totales_a_float(totales)}


def _totales_a_float(t: dict) -> dict:
    b = t["beneficio"]
    return {
        "subtotal": float(t["subtotal"]),
        "descuento": float(t["descuento"]),
        "total": float(t["total"]),
        "cantidad_articulos": t["cantidad_articulos"],
        "beneficio": {**b, "porcentaje": float(b["porcentaje"]),
                      "compra_minima": float(b["compra_minima"]),
                      "falta_para_aplicar": float(b["falta_para_aplicar"])},
    }


def agregar(db: Session, usuario_id: str, producto_id: str, cantidad: int) -> dict:
    producto = _producto_o_error(producto_id)
    carrito = _carrito(db, usuario_id)
    item = _item(carrito, producto["id"])
    nueva = (item.cantidad if item else 0) + cantidad
    _validar_stock(producto, nueva)

    if item:
        item.cantidad = nueva
    else:
        item = CarritoItem(producto_id=producto["id"], cantidad=nueva, nombre="", precio_unitario=0)
        carrito.items.append(item)
    # Siempre se guarda el nombre y precio vigentes del catálogo (nunca los del cliente)
    item.nombre = producto["nombre"]
    item.precio_unitario = producto["precio"]
    db.commit()
    return ver_carrito(db, usuario_id)


def cambiar_cantidad(db: Session, usuario_id: str, producto_id: str, cantidad: int) -> dict:
    carrito = _carrito(db, usuario_id)
    item = _item(carrito, producto_id)
    if item is None:
        raise ErrorCarrito(404, "Ese producto no está en tu carrito.")
    if cantidad == 0:
        carrito.items.remove(item)
    else:
        producto = _producto_o_error(producto_id)
        _validar_stock(producto, cantidad)
        item.cantidad = cantidad
        item.nombre = producto["nombre"]
        item.precio_unitario = producto["precio"]
    db.commit()
    return ver_carrito(db, usuario_id)


def eliminar(db: Session, usuario_id: str, producto_id: str) -> dict:
    return cambiar_cantidad(db, usuario_id, producto_id, 0)


def vaciar(db: Session, usuario_id: str) -> dict:
    carrito = _carrito(db, usuario_id)
    carrito.items.clear()
    db.commit()
    return ver_carrito(db, usuario_id)


# ---------------------------------------------------------------- compra
def _nuevo_codigo() -> str:
    return f"PED-{datetime.now(timezone.utc):%Y%m%d}-{secrets.token_hex(3).upper()}"


def confirmar_pedido(db: Session, usuario_id: str, total_esperado: float | None) -> dict:
    carrito = _carrito(db, usuario_id)
    if not carrito.items:
        raise ErrorCarrito(400, "Tu carrito está vacío.")

    # 1. Validar productos, stock y precios contra el catálogo
    problemas, precios_actualizados = [], False
    for it in carrito.items:
        producto = integraciones.obtener_producto(it.producto_id)
        if producto is None:
            problemas.append(f"'{it.nombre}' ya no está disponible.")
            continue
        if producto["stock"] is not None and it.cantidad > producto["stock"]:
            problemas.append(f"'{it.nombre}': solo hay {producto['stock']} unidades.")
        if _dec(producto["precio"]) != _dec(it.precio_unitario):
            it.precio_unitario = producto["precio"]
            precios_actualizados = True
    if problemas:
        db.commit()
        raise ErrorCarrito(409, "Revisa tu carrito antes de confirmar.",
                           {"problemas": problemas, "carrito": ver_carrito(db, usuario_id)})
    if precios_actualizados:
        db.commit()
        raise ErrorCarrito(409, "Algunos precios cambiaron. Revisa el nuevo total.",
                           {"carrito": ver_carrito(db, usuario_id)})

    # 2. Recalcular en el servidor con el segmento real del usuario
    segmento = integraciones.obtener_segmento(db, usuario_id)
    lineas = [Linea(i.producto_id, i.nombre, _dec(i.precio_unitario), i.cantidad) for i in carrito.items]
    totales = calcular_totales(lineas, segmento)

    if total_esperado is not None and _dec(total_esperado) != totales["total"]:
        raise ErrorCarrito(409, "El total cambió. Revisa el resumen antes de confirmar.",
                           {"carrito": ver_carrito(db, usuario_id)})

    # 3. Registrar el pedido y vaciar el carrito (en una sola transacción)
    beneficio = totales["beneficio"]
    pedido = Pedido(
        codigo=_nuevo_codigo(),
        usuario_id=usuario_id,
        segmento=beneficio["segmento"],
        porcentaje_descuento=beneficio["porcentaje"] if beneficio["aplicado"] else Decimal("0"),
        subtotal=totales["subtotal"],
        descuento=totales["descuento"],
        total=totales["total"],
        estado="confirmado",
        items=[PedidoItem(producto_id=l.producto_id, nombre=l.nombre, precio_unitario=l.precio_unitario,
                          cantidad=l.cantidad, importe=l.importe) for l in lineas],
    )
    db.add(pedido)
    carrito.items.clear()
    db.commit()
    db.refresh(pedido)

    return {
        "mensaje": f"¡Pedido {pedido.codigo} confirmado! Total pagado: {totales['total']}"
                   + (f" (ahorraste {totales['descuento']} por ser cliente {beneficio['segmento']})."
                      if totales["descuento"] > 0 else "."),
        "pedido": _pedido_a_dict(pedido),
    }


def _pedido_a_dict(p: Pedido) -> dict:
    return {
        "codigo": p.codigo,
        "estado": p.estado,
        "creado": p.creado,
        "segmento": p.segmento,
        "porcentaje_descuento": float(p.porcentaje_descuento),
        "subtotal": float(p.subtotal),
        "descuento": float(p.descuento),
        "total": float(p.total),
        "items": [{
            "producto_id": i.producto_id, "nombre": i.nombre,
            "precio_unitario": float(i.precio_unitario), "cantidad": i.cantidad,
            "importe": float(i.importe),
        } for i in p.items],
    }


def historial(db: Session, usuario_id: str) -> list[dict]:
    pedidos = db.scalars(
        select(Pedido).where(Pedido.usuario_id == usuario_id).order_by(Pedido.creado.desc())
    ).all()
    return [{
        "codigo": p.codigo, "estado": p.estado, "creado": p.creado, "total": float(p.total),
        "cantidad_articulos": sum(i.cantidad for i in p.items),
    } for p in pedidos]


def detalle_pedido(db: Session, usuario_id: str, codigo: str) -> dict:
    pedido = db.scalar(select(Pedido).where(Pedido.codigo == codigo, Pedido.usuario_id == usuario_id))
    if pedido is None:
        raise ErrorCarrito(404, "Pedido no encontrado.")
    return _pedido_a_dict(pedido)
