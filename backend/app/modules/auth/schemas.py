"""Formas de los datos que entran y salen de los endpoints de autenticación."""
import re

from pydantic import BaseModel, field_validator

_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegistroIn(BaseModel):
    nombre: str
    correo: str
    contrasena: str
    customer_id: int | None = None  # opcional: ID histórico si ya era cliente

    @field_validator("nombre")
    @classmethod
    def _nombre(cls, v):
        v = " ".join(v.split())
        if len(v) < 2:
            raise ValueError("Escribe tu nombre.")
        return v

    @field_validator("correo")
    @classmethod
    def _correo(cls, v):
        v = v.strip().lower()
        if not _CORREO.match(v):
            raise ValueError("Escribe un correo válido.")
        return v

    @field_validator("contrasena")
    @classmethod
    def _contrasena(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if len(v) > 64:
            raise ValueError("La contraseña no puede superar 64 caracteres.")
        return v


class LoginIn(BaseModel):
    correo: str
    contrasena: str


class Beneficio(BaseModel):
    segmento: str
    porcentaje: float
    compra_minima: float
    tope: float | None = None
    descripcion: str


class Perfil(BaseModel):
    id: int
    nombre: str
    correo: str
    customer_id: int | None = None
    segmento: str
    es_nuevo: bool  # True = sin coincidencia histórica (categoría comercial provisional)
    beneficio: Beneficio
