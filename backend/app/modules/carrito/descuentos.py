"""Beneficios por segmento de cliente.

Los nombres de segmento deben coincidir con los que produce el modelo K-Means
(tabla gold_clientes_segmentados en Neon; política en gold_politica_segmentos).
"Nuevo" no viene del K-Means: es la categoría provisional para clientes sin historial.
"""
from decimal import Decimal
import unicodedata

SEGMENTO_POR_DEFECTO = "Nuevo"

# porcentaje: descuento sobre el subtotal
# compra_minima: subtotal mínimo para que aplique (0 = siempre)
# tope: descuento máximo en dinero (None = sin tope)
BENEFICIOS = {
    "Campeones": {
        "porcentaje": Decimal("5"),
        "compra_minima": Decimal("0"),
        "tope": None,
        "descripcion": "5% de descuento en toda la compra por ser de nuestros mejores clientes.",
    },
    "En riesgo": {
        "porcentaje": Decimal("15"),
        "compra_minima": Decimal("100"),
        "tope": None,
        "descripcion": "15% de descuento en compras desde £100.",
    },
    "Prometedores": {
        "porcentaje": Decimal("10"),
        "compra_minima": Decimal("50"),
        "tope": None,
        "descripcion": "10% de descuento en compras desde £50.",
    },
    "Perdidos": {
        "porcentaje": Decimal("20"),
        "compra_minima": Decimal("150"),
        "tope": None,
        "descripcion": "20% de descuento en compras desde £150.",
    },
    "Nuevo": {
        "porcentaje": Decimal("5"),
        "compra_minima": Decimal("0"),
        "tope": Decimal("20"),
        "descripcion": "5% de descuento de bienvenida (máximo £20).",
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
