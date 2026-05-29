# tests/test_unitarias_menu.py
"""
NIVEL 1 — Pruebas Unitarias: clase Menu
Pipeline stage : Test › Unitarias
Cobertura      : agregar_item, obtener_precio, listar, eliminar_item
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from restaurante import Menu


class TestMenuAgregarItem(unittest.TestCase):
    """Pruebas para Menu.agregar_item()"""

    def setUp(self):
        self.menu = Menu()

    def test_agregar_item_nombre_y_precio_validos(self):
        self.menu.agregar_item("Bandeja paisa", 25000)
        self.assertIn("bandeja paisa", self.menu.listar())

    def test_agregar_item_precio_float(self):
        self.menu.agregar_item("Agua", 1500.50)
        self.assertEqual(self.menu.obtener_precio("Agua"), 1500.50)

    def test_agregar_item_sobreescribe_precio_existente(self):
        self.menu.agregar_item("Arepa", 2000)
        self.menu.agregar_item("Arepa", 3500)
        self.assertEqual(self.menu.obtener_precio("Arepa"), 3500)

    def test_agregar_item_nombre_vacio_lanza_valueerror(self):
        with self.assertRaises(ValueError) as ctx:
            self.menu.agregar_item("", 1000)
        self.assertIn("vacío", str(ctx.exception))

    def test_agregar_item_nombre_solo_espacios_lanza_valueerror(self):
        # Strings de solo espacios son falsy → deben lanzar ValueError
        with self.assertRaises(ValueError):
            self.menu.agregar_item("   ", 1000)

    def test_agregar_item_precio_cero_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.menu.agregar_item("Café", 0)

    def test_agregar_item_precio_negativo_lanza_valueerror(self):
        with self.assertRaises(ValueError):
            self.menu.agregar_item("Café", -500)

    def test_agregar_item_precio_muy_alto_es_valido(self):
        self.menu.agregar_item("Langosta", 500000)
        self.assertEqual(self.menu.obtener_precio("Langosta"), 500000)


class TestMenuObtenerPrecio(unittest.TestCase):
    """Pruebas para Menu.obtener_precio()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Churrasco", 45000)

    def test_obtener_precio_item_existente(self):
        self.assertEqual(self.menu.obtener_precio("Churrasco"), 45000)

    def test_obtener_precio_case_insensitive_mayusculas(self):
        self.assertEqual(self.menu.obtener_precio("CHURRASCO"), 45000)

    def test_obtener_precio_case_insensitive_minusculas(self):
        self.assertEqual(self.menu.obtener_precio("churrasco"), 45000)

    def test_obtener_precio_case_insensitive_mixto(self):
        self.assertEqual(self.menu.obtener_precio("ChUrRaScO"), 45000)

    def test_obtener_precio_item_inexistente_lanza_keyerror(self):
        with self.assertRaises(KeyError):
            self.menu.obtener_precio("Tacos")


class TestMenuListar(unittest.TestCase):
    """Pruebas para Menu.listar()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Pizza", 28000)
        self.menu.agregar_item("Gaseosa", 4000)

    def test_listar_retorna_cantidad_correcta(self):
        self.assertEqual(len(self.menu.listar()), 2)

    def test_listar_menu_vacio_retorna_dict_vacio(self):
        menu_vacio = Menu()
        self.assertEqual(menu_vacio.listar(), {})

    def test_listar_retorna_copia_no_referencia(self):
        copia = self.menu.listar()
        copia["intruso"] = 99999
        self.assertNotIn("intruso", self.menu.listar())

    def test_listar_claves_en_minusculas(self):
        claves = list(self.menu.listar().keys())
        for clave in claves:
            self.assertEqual(clave, clave.lower())


class TestMenuEliminarItem(unittest.TestCase):
    """Pruebas para Menu.eliminar_item()"""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Jugo de lulo", 5000)
        self.menu.agregar_item("Sancocho", 18000)

    def test_eliminar_item_existente(self):
        self.menu.eliminar_item("Jugo de lulo")
        self.assertNotIn("jugo de lulo", self.menu.listar())

    def test_eliminar_item_reduce_cantidad(self):
        self.menu.eliminar_item("Sancocho")
        self.assertEqual(len(self.menu.listar()), 1)

    def test_eliminar_item_inexistente_lanza_keyerror(self):
        with self.assertRaises(KeyError):
            self.menu.eliminar_item("Tamal")

    def test_eliminar_todos_los_items(self):
        self.menu.eliminar_item("Jugo de lulo")
        self.menu.eliminar_item("Sancocho")
        self.assertEqual(self.menu.listar(), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
