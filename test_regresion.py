# tests/test_regresion.py
"""
NIVEL 3 — Pruebas de Regresión
Pipeline stage : Test › Regresión
Propósito      : Asegurar que correcciones pasadas no vuelvan a fallar.
Cada clase documenta el bug específico que previene con su número de ticket.

  REG-001: precio_cero aceptado silenciosamente (corregido v0.2)
  REG-002: obtener_precio no era case-insensitive (corregido v0.3)
  REG-003: listar() devolvía referencia directa al dict interno (corregido v0.4)
  REG-004: agregar() con cantidad negativa no lanzaba error (corregido v0.5)
  REG-005: subtotal() fallaba con items acumulados en dos llamadas (corregido v0.6)
  REG-006: resumen() no incluía clave impuesto_19% (corregido v0.7)
  REG-007: quitar() eliminaba silenciosamente items inexistentes (corregido v0.8)
  REG-008: agregar() aceptaba nombre de item no registrado en menu (corregido v0.9)
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from restaurante import Menu, Pedido


class TestRegresion_REG001_PrecioCero(unittest.TestCase):
    """
    REG-001: Menu.agregar_item() aceptaba precio=0 sin lanzar error,
    lo que permitía items "gratis" por error de datos.
    """

    def test_precio_exactamente_cero_lanza_error(self):
        menu = Menu()
        with self.assertRaises(ValueError):
            menu.agregar_item("Agua gratis", 0)

    def test_precio_cero_punto_cero_lanza_error(self):
        menu = Menu()
        with self.assertRaises(ValueError):
            menu.agregar_item("Item", 0.0)


class TestRegresion_REG002_CaseInsensitive(unittest.TestCase):
    """
    REG-002: obtener_precio() era sensible a mayúsculas/minúsculas,
    por lo que "PIZZA" y "pizza" eran tratados como items distintos.
    """

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Pizza Hawaiana", 28000)

    def test_busqueda_en_mayusculas_encuentra_item(self):
        self.assertEqual(self.menu.obtener_precio("PIZZA HAWAIANA"), 28000)

    def test_busqueda_en_minusculas_encuentra_item(self):
        self.assertEqual(self.menu.obtener_precio("pizza hawaiana"), 28000)

    def test_busqueda_mixta_encuentra_item(self):
        self.assertEqual(self.menu.obtener_precio("Pizza HAWAIANA"), 28000)

    def test_agregar_en_mayusculas_no_duplica_item(self):
        self.menu.agregar_item("PIZZA HAWAIANA", 28000)
        self.assertEqual(len(self.menu.listar()), 1)


class TestRegresion_REG003_ListarEsCopia(unittest.TestCase):
    """
    REG-003: listar() devolvía el dict interno directamente,
    permitiendo modificarlo desde afuera y corromper el estado del Menu.
    """

    def test_modificar_resultado_listar_no_altera_menu(self):
        menu = Menu()
        menu.agregar_item("Sopa", 8000)
        externo = menu.listar()
        externo["sopa"] = 999999     # intenta corromper
        self.assertEqual(menu.obtener_precio("Sopa"), 8000)

    def test_agregar_a_resultado_listar_no_agrega_al_menu(self):
        menu = Menu()
        menu.agregar_item("Arroz", 4000)
        externo = menu.listar()
        externo["nuevo_item"] = 1000
        self.assertNotIn("nuevo_item", menu.listar())


class TestRegresion_REG004_CantidadNegativa(unittest.TestCase):
    """
    REG-004: Pedido.agregar() con cantidad negativa no validaba el valor,
    lo que generaba subtotales negativos incorrectos.
    """

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Empanada", 2000)
        self.pedido = Pedido(self.menu)

    def test_cantidad_negativa_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.pedido.agregar("Empanada", -1)

    def test_cantidad_menos_cien_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.pedido.agregar("Empanada", -100)

    def test_cantidad_cero_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.pedido.agregar("Empanada", 0)


class TestRegresion_REG005_AcumulacionCantidades(unittest.TestCase):
    """
    REG-005: subtotal() ignoraba las cantidades acumuladas en llamadas
    repetidas a agregar(), calculando solo la última cantidad.
    """

    def test_acumular_tres_veces_mismo_item_subtotal_correcto(self):
        menu = Menu()
        menu.agregar_item("Tinto", 1000)
        pedido = Pedido(menu)
        pedido.agregar("Tinto", 2)
        pedido.agregar("Tinto", 3)
        pedido.agregar("Tinto", 1)
        # Total cantidad: 6 → subtotal: 6000
        self.assertEqual(pedido.resumen()["items"]["tinto"], 6)
        self.assertEqual(pedido.subtotal(), 6000)


class TestRegresion_REG006_ClaveImpuestoResumen(unittest.TestCase):
    """
    REG-006: resumen() no incluía la clave 'impuesto_19%', lo que hacía
    fallar cualquier código que dependiera de ella.
    """

    def test_resumen_siempre_incluye_impuesto(self):
        menu = Menu()
        menu.agregar_item("Café", 3000)
        pedido = Pedido(menu)
        pedido.agregar("Café", 1)
        self.assertIn("impuesto_19%", pedido.resumen())

    def test_resumen_pedido_vacio_incluye_impuesto_en_cero(self):
        menu = Menu()
        pedido = Pedido(menu)
        self.assertIn("impuesto_19%", pedido.resumen())
        self.assertEqual(pedido.resumen()["impuesto_19%"], 0.0)


class TestRegresion_REG007_QuitarItemInexistente(unittest.TestCase):
    """
    REG-007: Pedido.quitar() no lanzaba error al intentar quitar un
    item no presente en el pedido; fallaba en silencio.
    """

    def test_quitar_item_nunca_agregado_lanza_keyerror(self):
        menu = Menu()
        menu.agregar_item("Limonada", 5000)
        pedido = Pedido(menu)
        with self.assertRaises(KeyError):
            pedido.quitar("Limonada")

    def test_quitar_item_ya_quitado_lanza_keyerror(self):
        menu = Menu()
        menu.agregar_item("Pan", 1500)
        pedido = Pedido(menu)
        pedido.agregar("Pan", 2)
        pedido.quitar("Pan")
        with self.assertRaises(KeyError):
            pedido.quitar("Pan")   # segundo intento debe lanzar error


class TestRegresion_REG008_ItemNoEnMenu(unittest.TestCase):
    """
    REG-008: Pedido.agregar() aceptaba items que no existían en el Menu,
    lo que hacía fallar el subtotal() al intentar obtener su precio.
    """

    def test_agregar_item_inexistente_lanza_keyerror_inmediatamente(self):
        menu = Menu()
        menu.agregar_item("Tamal", 7000)
        pedido = Pedido(menu)
        with self.assertRaises(KeyError):
            pedido.agregar("Bandeja paisa")   # no está en el menú

    def test_error_al_agregar_no_deja_item_en_pedido(self):
        menu = Menu()
        menu.agregar_item("Tamal", 7000)
        pedido = Pedido(menu)
        try:
            pedido.agregar("Inexistente")
        except KeyError:
            pass
        self.assertNotIn("inexistente", pedido.resumen()["items"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
