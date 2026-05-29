# tests/test_unitarias_pedido.py
"""
NIVEL 1 — Pruebas Unitarias: clase Pedido
Pipeline stage : Test › Unitarias
Cobertura      : agregar, quitar, subtotal, impuesto, total, resumen
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from restaurante import Menu, Pedido


class TestPedidoAgregar(unittest.TestCase):
    """Pruebas para Pedido.agregar()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Pizza", 30000)
        self.menu.agregar_item("Gaseosa", 4000)
        self.pedido = Pedido(self.menu)

    def test_agregar_item_aparece_en_resumen(self):
        self.pedido.agregar("Pizza")
        self.assertIn("pizza", self.pedido.resumen()["items"])

    def test_agregar_cantidad_default_es_uno(self):
        self.pedido.agregar("Pizza")
        self.assertEqual(self.pedido.resumen()["items"]["pizza"], 1)

    def test_agregar_cantidad_explicita(self):
        self.pedido.agregar("Pizza", 4)
        self.assertEqual(self.pedido.resumen()["items"]["pizza"], 4)

    def test_agregar_mismo_item_dos_veces_acumula(self):
        self.pedido.agregar("Gaseosa", 2)
        self.pedido.agregar("Gaseosa", 3)
        self.assertEqual(self.pedido.resumen()["items"]["gaseosa"], 5)

    def test_agregar_cantidad_cero_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.pedido.agregar("Pizza", 0)

    def test_agregar_cantidad_negativa_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.pedido.agregar("Pizza", -1)

    def test_agregar_item_no_en_menu_lanza_keyerror(self):
        with self.assertRaises(KeyError):
            self.pedido.agregar("Sushi")

    def test_agregar_multiples_items_diferentes(self):
        self.pedido.agregar("Pizza", 1)
        self.pedido.agregar("Gaseosa", 2)
        self.assertEqual(len(self.pedido.resumen()["items"]), 2)


class TestPedidoQuitar(unittest.TestCase):
    """Pruebas para Pedido.quitar()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Hamburguesa", 22000)
        self.menu.agregar_item("Papas fritas", 8000)
        self.pedido = Pedido(self.menu)
        self.pedido.agregar("Hamburguesa", 2)
        self.pedido.agregar("Papas fritas", 1)

    def test_quitar_item_existente(self):
        self.pedido.quitar("Hamburguesa")
        self.assertNotIn("hamburguesa", self.pedido.resumen()["items"])

    def test_quitar_item_reduce_cantidad_total(self):
        self.pedido.quitar("Papas fritas")
        self.assertEqual(len(self.pedido.resumen()["items"]), 1)

    def test_quitar_item_inexistente_lanza_keyerror(self):
        with self.assertRaises(KeyError):
            self.pedido.quitar("Perro caliente")

    def test_quitar_todos_los_items_deja_pedido_vacio(self):
        self.pedido.quitar("Hamburguesa")
        self.pedido.quitar("Papas fritas")
        self.assertEqual(self.pedido.resumen()["items"], {})


class TestPedidoCalculos(unittest.TestCase):
    """Pruebas para subtotal(), impuesto(), total()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Filete", 60000)
        self.menu.agregar_item("Vino", 35000)
        self.pedido = Pedido(self.menu)

    def test_subtotal_pedido_vacio_es_cero(self):
        self.assertEqual(self.pedido.subtotal(), 0.0)

    def test_subtotal_un_item_una_cantidad(self):
        self.pedido.agregar("Filete", 1)
        self.assertEqual(self.pedido.subtotal(), 60000)

    def test_subtotal_un_item_multiples_cantidades(self):
        self.pedido.agregar("Filete", 3)
        self.assertEqual(self.pedido.subtotal(), 180000)

    def test_subtotal_varios_items(self):
        self.pedido.agregar("Filete", 1)   # 60000
        self.pedido.agregar("Vino", 2)     # 70000
        self.assertEqual(self.pedido.subtotal(), 130000)

    def test_impuesto_19_porciento_exacto(self):
        self.pedido.agregar("Filete", 1)   # 60000 × 0.19 = 11400
        self.assertAlmostEqual(self.pedido.impuesto(), 11400, places=2)

    def test_impuesto_pedido_vacio_es_cero(self):
        self.assertEqual(self.pedido.impuesto(), 0.0)

    def test_total_es_subtotal_mas_impuesto(self):
        self.pedido.agregar("Filete", 1)
        esperado = round(60000 * 1.19, 2)
        self.assertEqual(self.pedido.total(), esperado)

    def test_total_pedido_vacio_es_cero(self):
        self.assertEqual(self.pedido.total(), 0.0)

    def test_total_redondeado_dos_decimales(self):
        self.menu.agregar_item("Agua", 1000)
        self.pedido.agregar("Agua", 3)     # 3000 × 1.19 = 3570.00 (exacto)
        total = self.pedido.total()
        self.assertEqual(total, round(total, 2))


class TestPedidoResumen(unittest.TestCase):
    """Pruebas para Pedido.resumen()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Ceviche", 32000)
        self.pedido = Pedido(self.menu)
        self.pedido.agregar("Ceviche", 2)

    def test_resumen_contiene_clave_items(self):
        self.assertIn("items", self.pedido.resumen())

    def test_resumen_contiene_clave_subtotal(self):
        self.assertIn("subtotal", self.pedido.resumen())

    def test_resumen_contiene_clave_impuesto(self):
        self.assertIn("impuesto_19%", self.pedido.resumen())

    def test_resumen_contiene_clave_total(self):
        self.assertIn("total", self.pedido.resumen())

    def test_resumen_valores_coherentes(self):
        r = self.pedido.resumen()
        self.assertEqual(r["subtotal"] + r["impuesto_19%"], r["total"])

    def test_resumen_items_es_copia(self):
        r = self.pedido.resumen()
        r["items"]["intruso"] = 99
        self.assertNotIn("intruso", self.pedido.resumen()["items"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
