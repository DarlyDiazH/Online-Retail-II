from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from .schemas import Producto, RespuestaCatalogo
from .service import (
    consultar_disponibilidad,
    listar_categorias,
    obtener_producto_por_id,
    obtener_productos,
)


router = APIRouter(prefix="/catalogo", tags=["Catálogo"])


@router.get("/productos", response_model=RespuestaCatalogo)
def get_productos(
    busqueda: Optional[str] = Query(default=None, description="Buscar por nombre, descripción o código"),
    categoria: Optional[str] = Query(default=None, description="Filtrar por categoría exacta"),
    solo_disponibles: bool = Query(default=False, description="Mostrar solo productos con stock disponible"),
):
    productos = obtener_productos(
        busqueda=busqueda,
        categoria=categoria,
        solo_disponibles=solo_disponibles,
    )
    return RespuestaCatalogo(total=len(productos), productos=productos)


@router.get("/categorias", response_model=list[str])
def get_categorias():
    return listar_categorias()


@router.get("/productos/{producto_id}", response_model=Producto)
def get_producto(producto_id: str):
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/productos/{producto_id}/disponibilidad")
def get_disponibilidad(
    producto_id: str,
    cantidad: int = Query(default=1, ge=1, description="Cantidad a consultar"),
):
    info = consultar_disponibilidad(producto_id=producto_id, cantidad=cantidad)
    if not info:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return info