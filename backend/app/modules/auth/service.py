"""Reglas de registro, inicio de sesión y perfil.

Reutiliza del módulo de carrito (sin duplicarlo):
- obtener_segmento(): lee el segmento del usuario en Neon (variable SEGMENTO_SQL del .env).
- beneficio_de(): el descuento que corresponde a ese segmento.
"""
import logging
import os

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.modules.carrito.descuentos import SEGMENTO_POR_DEFECTO, beneficio_de
from app.modules.carrito.integraciones import obtener_segmento

from . import schemas, seguridad
from .models import Usuario

log = logging.getLogger(__name__)


class ErrorAuth(Exception):
    def __init__(self, estado: int, mensaje: str, campo: str | None = None):
        self.estado, self.mensaje, self.campo = estado, mensaje, campo


def _cliente_historico_existe(db: Session, customer_id: int) -> bool:
    """¿Existe ese Customer_ID en la tabla de clientes segmentados (Neon)?

    La consulta se puede cambiar con CLIENTE_SQL en el .env (debe recibir :customer_id).
    """
    consulta = os.getenv("CLIENTE_SQL") or "SELECT 1 FROM vw_descuentos_checkout WHERE customer_id = :customer_id"
    try:
        return db.execute(text(consulta), {"customer_id": customer_id}).first() is not None
    except Exception as e:  # la tabla aún no existe, columna distinta, etc.
        log.warning("No se pudo consultar el cliente histórico (%s)", e)
        db.rollback()
        return False


def _perfil(db: Session, usuario: Usuario) -> schemas.Perfil:
    segmento = obtener_segmento(db, str(usuario.id))
    return schemas.Perfil(
        id=usuario.id,
        nombre=usuario.nombre,
        correo=usuario.correo,
        customer_id=usuario.customer_id,
        segmento=segmento,
        es_nuevo=usuario.customer_id is None,
        beneficio=beneficio_de(segmento),
    )


def registrar(db: Session, datos: schemas.RegistroIn) -> schemas.Perfil:
    if db.scalar(select(Usuario).where(Usuario.correo == datos.correo)):
        raise ErrorAuth(409, "Este correo ya está registrado.", "correo")

    if datos.customer_id is not None:
        if not _cliente_historico_existe(db, datos.customer_id):
            raise ErrorAuth(400, "No encontramos ese ID de cliente. Revísalo o déjalo vacío.", "customer_id")
        if db.scalar(select(Usuario).where(Usuario.customer_id == datos.customer_id)):
            raise ErrorAuth(409, "Ese ID de cliente ya está vinculado a otra cuenta.", "customer_id")

    usuario = Usuario(
        nombre=datos.nombre,
        correo=datos.correo,
        password_hash=seguridad.hashear(datos.contrasena),
        customer_id=datos.customer_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return _perfil(db, usuario)


def iniciar_sesion(db: Session, datos: schemas.LoginIn) -> schemas.Perfil:
    usuario = db.scalar(select(Usuario).where(Usuario.correo == datos.correo.strip().lower()))
    if not usuario or not seguridad.verificar(datos.contrasena, usuario.password_hash):
        raise ErrorAuth(401, "Correo o contraseña incorrectos.")
    return _perfil(db, usuario)


def ver_perfil(db: Session, usuario_id: str) -> schemas.Perfil:
    usuario = db.get(Usuario, int(usuario_id)) if usuario_id.isdigit() else None
    if not usuario:
        raise ErrorAuth(401, "Debes iniciar sesión.")
    return _perfil(db, usuario)
