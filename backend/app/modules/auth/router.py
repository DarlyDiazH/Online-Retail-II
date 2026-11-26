"""Endpoints de registro, inicio de sesión y perfil.

La identificación sigue el contrato del módulo de carrito: el frontend guarda el id
del usuario y lo envía en la cabecera X-Usuario-Id (alcance académico, sin tokens).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.carrito.router import usuario_actual

from . import schemas, service

router = APIRouter(prefix="/api/auth", tags=["Autenticación y perfil"])


def _ejecutar(funcion, *args):
    try:
        return funcion(*args)
    except service.ErrorAuth as e:
        raise HTTPException(e.estado, {"mensaje": e.mensaje, "campo": e.campo})


@router.post("/registro", response_model=schemas.Perfil, status_code=201)
def registro(datos: schemas.RegistroIn, db: Session = Depends(get_db)):
    return _ejecutar(service.registrar, db, datos)


@router.post("/login", response_model=schemas.Perfil)
def login(datos: schemas.LoginIn, db: Session = Depends(get_db)):
    return _ejecutar(service.iniciar_sesion, db, datos)


@router.get("/perfil", response_model=schemas.Perfil)
def perfil(usuario: str = Depends(usuario_actual), db: Session = Depends(get_db)):
    return _ejecutar(service.ver_perfil, db, usuario)
