"""Tabla de usuarios (cuentas de la aplicación). Se crea sola en Neon al iniciar la API."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _ahora():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    # user_id: identifica la CUENTA creada en la aplicación
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    # Customer_ID histórico de Online Retail II. Vacío = cliente sin coincidencia ("Nuevo").
    # El segmento NO se guarda aquí: se consulta en la tabla de clientes segmentados.
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)
