# tests/test_smoke.py
"""
NIVEL 4 — Pruebas de Humo (Smoke Tests)
Pipeline stage : Deploy › Smoke
Propósito      : Verificación rápida post-deploy que el sistema arranca
                 y sus funciones críticas responden correctamente.
                 Si alguna falla, el deploy se revierte.

Criterio       : Cada prueba debe ejecutarse en < 1 segundo.
Cobertura      : Solo caminos felices (happy path) de las funciones críticas.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSmokeImportacion(unittest.TestCase):
    """Smoke 1: El módulo y sus clases importan sin errores."""

    def test_importar_modulo_restaurante(self):
        import restaurante
        self.assertIsNotNone(restaurante)

    def test_importar_clase_menu(self):
        from restaurante import Menu
        self.assertTrue(callable(Menu))

    def test_importar_clase_pedido(self):
        from restaurante import Pedido
        self.assertTrue(callable(Pedido))

    def test_importar_funcion_version(self):
        from restaurante import version
        self.assertTrue(callable(version))

    def test_version_retorna_string(self):
        from restaurante import version
        v = version()
        self.assertIsInstance(v, str)
        self.assertTrue(len(v) > 0)


class TestSmokeMenu(unittest.TestCase):
    """Smoke 2: Operaciones básicas de Menu funcionan."""

    def setUp(self):
        from restaurante import Menu
        self.menu = Menu()

    def test_menu_se_instancia(self):
        self.assertIsNotNone(self.menu)

    def test_agregar_item_funciona(self):
        self.menu.agregar_item("Producto A", 10000)
        self.assertIn("producto a", self.menu.listar())

    def test_obtener_precio_funciona(self):
        self.menu.agregar_item("Producto B", 20000)
        self.assertEqual(self.menu.obtener_precio("Producto B"), 20000)

    def test_listar_funciona(self):
        resultado = self.menu.listar()
        self.assertIsInstance(resultado, dict)

    def test_eliminar_item_funciona(self):
        self.menu.agregar_item("Producto C", 5000)
        self.menu.eliminar_item("Producto C")
        self.assertNotIn("producto c", self.menu.listar())


class TestSmokePedido(unittest.TestCase):
    """Smoke 3: Operaciones básicas de Pedido funcionan."""

    def setUp(self):
        from restaurante import Menu, Pedido
        self.menu = Menu()
        self.menu.agregar_item("Item test", 15000)
        self.pedido = Pedido(self.menu)

    def test_pedido_se_instancia(self):
        self.assertIsNotNone(self.pedido)

    def test_agregar_y_verificar_item(self):
        self.pedido.agregar("Item test", 1)
        self.assertIn("item test", self.pedido.resumen()["items"])

    def test_subtotal_retorna_numero(self):
        self.pedido.agregar("Item test", 1)
        self.assertIsInstance(self.pedido.subtotal(), float)

    def test_impuesto_mayor_que_cero(self):
        self.pedido.agregar("Item test", 1)
        self.assertGreater(self.pedido.impuesto(), 0)

    def test_total_mayor_que_subtotal(self):
        self.pedido.agregar("Item test", 1)
        self.assertGreater(self.pedido.total(), self.pedido.subtotal())

    def test_resumen_es_dict(self):
        self.assertIsInstance(self.pedido.resumen(), dict)


class TestSmokeFlujoMinimo(unittest.TestCase):
    """Smoke 4: Flujo mínimo de negocio de principio a fin."""

    def test_ciclo_completo_minimo(self):
        """
        Crea menú → crea pedido → agrega item → obtiene total.
        Si este test falla, el sistema no puede operar en absoluto.
        """
        from restaurante import Menu, Pedido

        menu = Menu()
        menu.agregar_item("Plato del día", 18000)

        pedido = Pedido(menu)
        pedido.agregar("Plato del día", 1)

        resumen = pedido.resumen()

        self.assertEqual(resumen["subtotal"], 18000)
        self.assertGreater(resumen["total"], 18000)
        self.assertGreater(resumen["impuesto_19%"], 0)

    def test_version_y_modulo_consistentes(self):
        from restaurante import version, VERSION
        self.assertEqual(version(), VERSION)


if __name__ == "__main__":
    unittest.main(verbosity=2)
