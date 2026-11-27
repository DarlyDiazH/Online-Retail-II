"""Endpoints del carrito y pedidos.

Identificación del usuario: por ahora se envía en la cabecera `X-Usuario-Id`.
Cuando el módulo de autenticación (Persona 1) tenga su dependencia que lee el
token (p. ej. `obtener_usuario_actual`), se reemplaza `usuario_actual` por ella.
"""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from . import schemas, service

router = APIRouter(prefix="/api", tags=["Carrito y compras"])


def usuario_actual(x_usuario_id: str = Header(..., alias="X-Usuario-Id")) -> str:
    usuario_id = x_usuario_id.strip()
    if not usuario_id:
        raise HTTPException(401, "Debes iniciar sesión.")
    return usuario_id


def _ejecutar(funcion, *args):
    try:
        return funcion(*args)
    except service.ErrorCarrito as e:
        raise HTTPException(e.estado, {"mensaje": e.mensaje, **e.detalle})


# ---------- Carrito ----------
@router.get("/carrito", response_model=schemas.Carrito)
def ver_carrito(usuario: str = Depends(usuario_actual), db: Session = Depends(get_db)):
    return _ejecutar(service.ver_carrito, db, usuario)


@router.post("/carrito/items", response_model=schemas.Carrito)
def agregar_item(datos: schemas.AgregarItem, usuario: str = Depends(usuario_actual),
                 db: Session = Depends(get_db)):
    return _ejecutar(service.agregar, db, usuario, datos.producto_id, datos.cantidad)


@router.put("/carrito/items/{producto_id}", response_model=schemas.Carrito)
def cambiar_cantidad(producto_id: str, datos: schemas.CambiarCantidad,
                     usuario: str = Depends(usuario_actual), db: Session = Depends(get_db)):
    return _ejecutar(service.cambiar_cantidad, db, usuario, producto_id, datos.cantidad)


@router.delete("/carrito/items/{producto_id}", response_model=schemas.Carrito)
def eliminar_item(producto_id: str, usuario: str = Depends(usuario_actual),
                  db: Session = Depends(get_db)):
    return _ejecutar(service.eliminar, db, usuario, producto_id)


@router.delete("/carrito", response_model=schemas.Carrito)
def vaciar_carrito(usuario: str = Depends(usuario_actual), db: Session = Depends(get_db)):
    return _ejecutar(service.vaciar, db, usuario)


# ---------- Pedidos ----------
@router.post("/pedidos", response_model=schemas.Confirmacion, status_code=201)
def confirmar_pedido(datos: schemas.ConfirmarPedido, usuario: str = Depends(usuario_actual),
                     db: Session = Depends(get_db)):
    return _ejecutar(service.confirmar_pedido, db, usuario, datos.total_esperado)


@router.get("/pedidos", response_model=list[schemas.ResumenPedido])
def historial(usuario: str = Depends(usuario_actual), db: Session = Depends(get_db)):
    return _ejecutar(service.historial, db, usuario)


@router.get("/pedidos/{codigo}", response_model=schemas.Pedido)
def detalle_pedido(codigo: str, usuario: str = Depends(usuario_actual), db: Session = Depends(get_db)):
    return _ejecutar(service.detalle_pedido, db, usuario, codigo)
