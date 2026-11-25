"""Cálculo de subtotal, descuento y total. Sin dependencias externas para poder probarlo fácil."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from .descuentos import beneficio_de

CENTAVOS = Decimal("0.01")


def redondear(valor: Decimal) -> Decimal:
    return Decimal(valor).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


@dataclass
class Linea:
    producto_id: str
    nombre: str
    precio_unitario: Decimal
    cantidad: int

    @property
    def importe(self) -> Decimal:
        return redondear(Decimal(self.precio_unitario) * self.cantidad)


def calcular_totales(lineas: list[Linea], segmento: str | None) -> dict:
    """Calcula el resumen de compra aplicando el beneficio del segmento."""
    subtotal = redondear(sum((l.importe for l in lineas), Decimal("0")))
    beneficio = beneficio_de(segmento)

    descuento = Decimal("0")
    aplicado = bool(lineas) and subtotal >= beneficio["compra_minima"]
    if aplicado:
        descuento = redondear(subtotal * beneficio["porcentaje"] / Decimal("100"))
        if beneficio["tope"] is not None:
            descuento = min(descuento, beneficio["tope"])

    total = redondear(subtotal - descuento)
    return {
        "subtotal": subtotal,
        "descuento": descuento,
        "total": total,
        "cantidad_articulos": sum(l.cantidad for l in lineas),
        "beneficio": {
            "segmento": beneficio["segmento"],
            "porcentaje": beneficio["porcentaje"],
            "descripcion": beneficio["descripcion"],
            "compra_minima": beneficio["compra_minima"],
            "aplicado": aplicado,
            "falta_para_aplicar": (
                Decimal("0") if aplicado or not lineas
                else redondear(beneficio["compra_minima"] - subtotal)
            ),
        },
    }
