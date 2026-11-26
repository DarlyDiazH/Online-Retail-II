"""Beneficios por segmento de cliente.

Los nombres de segmento deben coincidir con los que produce el modelo K-Means
(guardados en Neon por el módulo de autenticación). Si el equipo usa otros
nombres, solo hay que editar el diccionario BENEFICIOS.
"""
from decimal import Decimal
import unicodedata

SEGMENTO_POR_DEFECTO = "Nuevo"

# porcentaje: descuento sobre el subtotal
# compra_minima: subtotal mínimo para que aplique (0 = siempre)
# tope: descuento máximo en dinero (None = sin tope)
BENEFICIOS = {
    "VIP": {
        "porcentaje": Decimal("15"),
        "compra_minima": Decimal("0"),
        "tope": None,
        "descripcion": "15% de descuento en toda la compra por ser cliente VIP.",
    },
    "Leal": {
        "porcentaje": Decimal("10"),
        "compra_minima": Decimal("0"),
        "tope": None,
        "descripcion": "10% de descuento por tu fidelidad.",
    },
    "Potencial": {
        "porcentaje": Decimal("7"),
        "compra_minima": Decimal("30"),
        "tope": None,
        "descripcion": "7% de descuento en compras desde 30.",
    },
    "En riesgo": {
        "porcentaje": Decimal("12"),
        "compra_minima": Decimal("0"),
        "tope": Decimal("50"),
        "descripcion": "12% de descuento (máximo 50) para darte la bienvenida de vuelta.",
    },
    "Nuevo": {
        "porcentaje": Decimal("5"),
        "compra_minima": Decimal("0"),
        "tope": Decimal("20"),
        "descripcion": "5% de descuento de bienvenida (máximo 20).",
    },
}


def _normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.lower().split())


_INDICE = {_normalizar(nombre): nombre for nombre in BENEFICIOS}


def resolver_segmento(segmento: str | None) -> str:
    """Devuelve el nombre oficial del segmento, o 'Nuevo' si no se reconoce."""
    if not segmento:
        return SEGMENTO_POR_DEFECTO
    return _INDICE.get(_normalizar(str(segmento)), SEGMENTO_POR_DEFECTO)


def beneficio_de(segmento: str | None) -> dict:
    nombre = resolver_segmento(segmento)
    return {"segmento": nombre, **BENEFICIOS[nombre]}
