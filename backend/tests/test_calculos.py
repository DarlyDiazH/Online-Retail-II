"""Pruebas de la lógica de precios. Ejecutar desde backend/:  python -m unittest -v"""
import unittest
from decimal import Decimal as D

from app.modules.carrito.calculos import Linea, calcular_totales
from app.modules.carrito.descuentos import resolver_segmento


class PruebasSegmento(unittest.TestCase):
    def test_nombres_flexibles(self):
        self.assertEqual(resolver_segmento("campeones"), "Campeones")
        self.assertEqual(resolver_segmento("  EN  RIESGO "), "En riesgo")
        self.assertEqual(resolver_segmento("Perdídos"), "Perdidos")

    def test_sin_coincidencia_es_nuevo(self):
        self.assertEqual(resolver_segmento(None), "Nuevo")
        self.assertEqual(resolver_segmento("desconocido"), "Nuevo")


class PruebasTotales(unittest.TestCase):
    def test_en_riesgo_15(self):
        r = calcular_totales([Linea("1", "A", D("52.75"), 2), Linea("2", "B", D("2.95"), 3)], "En riesgo")
        self.assertEqual(r["subtotal"], D("114.35"))
        self.assertEqual(r["descuento"], D("17.15"))  # 17.1525 -> 17.15
        self.assertEqual(r["total"], D("97.20"))
        self.assertEqual(r["cantidad_articulos"], 5)

    def test_tope_nuevo(self):
        r = calcular_totales([Linea("1", "A", D("500"), 1)], None)
        self.assertEqual(r["beneficio"]["segmento"], "Nuevo")
        self.assertEqual(r["descuento"], D("20"))
        self.assertEqual(r["total"], D("480.00"))

    def test_compra_minima_no_alcanzada(self):
        r = calcular_totales([Linea("1", "A", D("10"), 2)], "Prometedores")
        self.assertFalse(r["beneficio"]["aplicado"])
        self.assertEqual(r["descuento"], D("0"))
        self.assertEqual(r["beneficio"]["falta_para_aplicar"], D("30.00"))

    def test_carrito_vacio(self):
        r = calcular_totales([], "Campeones")
        self.assertEqual(r["total"], D("0.00"))
        self.assertFalse(r["beneficio"]["aplicado"])


if __name__ == "__main__":
    unittest.main()
