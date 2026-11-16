"""Pruebas de la lógica de precios. Ejecutar desde backend/:  python -m unittest -v"""
import unittest
from decimal import Decimal as D

from app.modules.carrito.calculos import Linea, calcular_totales
from app.modules.carrito.descuentos import resolver_segmento


class PruebasSegmento(unittest.TestCase):
    def test_nombres_flexibles(self):
        self.assertEqual(resolver_segmento("vip"), "VIP")
        self.assertEqual(resolver_segmento("  EN  RIESGO "), "En riesgo")
        self.assertEqual(resolver_segmento("Leál"), "Leal")

    def test_sin_coincidencia_es_nuevo(self):
        self.assertEqual(resolver_segmento(None), "Nuevo")
        self.assertEqual(resolver_segmento("desconocido"), "Nuevo")


class PruebasTotales(unittest.TestCase):
    def test_vip_15(self):
        r = calcular_totales([Linea("1", "A", D("12.75"), 2), Linea("2", "B", D("2.95"), 3)], "VIP")
        self.assertEqual(r["subtotal"], D("34.35"))
        self.assertEqual(r["descuento"], D("5.15"))  # 5.1525 -> 5.15
        self.assertEqual(r["total"], D("29.20"))
        self.assertEqual(r["cantidad_articulos"], 5)

    def test_tope_nuevo(self):
        r = calcular_totales([Linea("1", "A", D("500"), 1)], None)
        self.assertEqual(r["beneficio"]["segmento"], "Nuevo")
        self.assertEqual(r["descuento"], D("20"))
        self.assertEqual(r["total"], D("480.00"))

    def test_compra_minima_no_alcanzada(self):
        r = calcular_totales([Linea("1", "A", D("10"), 2)], "Potencial")
        self.assertFalse(r["beneficio"]["aplicado"])
        self.assertEqual(r["descuento"], D("0"))
        self.assertEqual(r["beneficio"]["falta_para_aplicar"], D("10.00"))

    def test_carrito_vacio(self):
        r = calcular_totales([], "VIP")
        self.assertEqual(r["total"], D("0.00"))
        self.assertFalse(r["beneficio"]["aplicado"])


if __name__ == "__main__":
    unittest.main()
