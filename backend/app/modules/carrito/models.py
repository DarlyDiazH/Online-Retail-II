"""Tablas del módulo de carrito y pedidos (se crean en Neon al iniciar la API)."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _ahora():
    return datetime.now(timezone.utc)


class Carrito(Base):
    __tablename__ = "carritos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)
    actualizado: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora, onupdate=_ahora)

    items: Mapped[list["CarritoItem"]] = relationship(
        back_populates="carrito", cascade="all, delete-orphan", order_by="CarritoItem.id"
    )


class CarritoItem(Base):
    __tablename__ = "carrito_items"
    __table_args__ = (UniqueConstraint("carrito_id", "producto_id", name="uq_carrito_producto"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    carrito_id: Mapped[int] = mapped_column(ForeignKey("carritos.id", ondelete="CASCADE"))
    producto_id: Mapped[str] = mapped_column(String(64))
    nombre: Mapped[str] = mapped_column(String(255))
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2))
    cantidad: Mapped[int] = mapped_column(Integer)

    carrito: Mapped[Carrito] = relationship(back_populates="items")


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    usuario_id: Mapped[str] = mapped_column(String(64), index=True)
    segmento: Mapped[str] = mapped_column(String(50))
    porcentaje_descuento: Mapped[float] = mapped_column(Numeric(5, 2))
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2))
    descuento: Mapped[float] = mapped_column(Numeric(12, 2))
    total: Mapped[float] = mapped_column(Numeric(12, 2))
    estado: Mapped[str] = mapped_column(String(20), default="confirmado")
    creado: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_ahora)

    items: Mapped[list["PedidoItem"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", order_by="PedidoItem.id"
    )


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id", ondelete="CASCADE"))
    producto_id: Mapped[str] = mapped_column(String(64))
    nombre: Mapped[str] = mapped_column(String(255))
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2))
    cantidad: Mapped[int] = mapped_column(Integer)
    importe: Mapped[float] = mapped_column(Numeric(12, 2))

    pedido: Mapped[Pedido] = relationship(back_populates="items")
