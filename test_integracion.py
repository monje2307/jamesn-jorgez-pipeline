# tests/test_integracion.py
"""
NIVEL 2 — Pruebas de Integración: Menu ↔ Pedido
Pipeline stage : Test › Integración
Verifica flujos end-to-end que combinan ambas clases:
  - Ciclo completo de un pedido de restaurante
  - Consistencia entre Menu modificado y Pedido activo
  - Múltiples pedidos independientes sobre el mismo menú
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from restaurante import Menu, Pedido


class TestFlujoCompletoRestaurante(unittest.TestCase):
    """Flujo de vida completo: crear menú → tomar pedido → cobrar."""

    def setUp(self):
        self.menu = Menu()
        self.menu.agregar_item("Bandeja paisa",  25000)
        self.menu.agregar_item("Jugo de lulo",    5000)
        self.menu.agregar_item("Postre del día",  9000)
        self.menu.agregar_item("Agua",            2000)

    def test_pedido_con_todos_los_items_del_menu(self):
        pedido = Pedido(self.menu)
        pedido.agregar("Bandeja paisa", 1)   # 25000
        pedido.agregar("Jugo de lulo",  1)   #  5000
        pedido.agregar("Postre del día",1)   #  9000
        pedido.agregar("Agua",          1)   #  2000
        self.assertEqual(pedido.subtotal(), 41000)
        self.assertAlmostEqual(pedido.impuesto(), round(41000 * 0.19, 2))
        self.assertEqual(pedido.total(), round(41000 * 1.19, 2))

    def test_agregar_y_luego_quitar_item_recalcula_total(self):
        pedido = Pedido(self.menu)
        pedido.agregar("Bandeja paisa", 2)   # 50000
        pedido.agregar("Agua", 3)            #  6000  → subtotal 56000
        pedido.quitar("Agua")                # quitar agua → subtotal 50000
        self.assertEqual(pedido.subtotal(), 50000)
        self.assertEqual(pedido.total(), round(50000 * 1.19, 2))

    def test_pedido_mesa_familiar_grande(self):
        pedido = Pedido(self.menu)
        pedido.agregar("Bandeja paisa",  4)  # 100000
        pedido.agregar("Jugo de lulo",   4)  #  20000
        pedido.agregar("Postre del día", 4)  #  36000
        pedido.agregar("Agua",           8)  #  16000
        self.assertEqual(pedido.subtotal(), 172000)

    def test_resumen_coherente_subtotal_mas_iva_igual_total(self):
        pedido = Pedido(self.menu)
        pedido.agregar("Bandeja paisa", 1)
        pedido.agregar("Jugo de lulo",  2)
        r = pedido.resumen()
        self.assertAlmostEqual(r["subtotal"] + r["impuesto_19%"], r["total"], places=2)


class TestConsistenciaMenuPedido(unittest.TestCase):
    """Verifica que cambios en el Menú se reflejan correctamente en nuevos Pedidos."""

    def test_item_eliminado_del_menu_no_disponible_en_nuevo_pedido(self):
        menu = Menu()
        menu.agregar_item("Sopa",  8000)
        menu.agregar_item("Arroz", 4000)
        menu.eliminar_item("Sopa")

        pedido = Pedido(menu)
        with self.assertRaises(KeyError):
            pedido.agregar("Sopa")

    def test_precio_actualizado_en_menu_refleja_en_pedido_nuevo(self):
        menu = Menu()
        menu.agregar_item("Café", 3000)
        menu.agregar_item("Café", 4500)   # actualiza precio

        pedido = Pedido(menu)
        pedido.agregar("Café", 2)
        self.assertEqual(pedido.subtotal(), 9000)   # 4500 × 2

    def test_menu_con_un_solo_item_pedido_funciona(self):
        menu = Menu()
        menu.agregar_item("Empanada", 2000)
        pedido = Pedido(menu)
        pedido.agregar("Empanada", 5)
        self.assertEqual(pedido.subtotal(), 10000)

    def test_dos_pedidos_sobre_mismo_menu_son_independientes(self):
        menu = Menu()
        menu.agregar_item("Pizza", 30000)
        menu.agregar_item("Refresco", 4000)

        mesa1 = Pedido(menu)
        mesa2 = Pedido(menu)

        mesa1.agregar("Pizza",    2)   # 60000
        mesa2.agregar("Refresco", 3)   # 12000

        self.assertEqual(mesa1.subtotal(), 60000)
        self.assertEqual(mesa2.subtotal(), 12000)
        # Modificar mesa1 no afecta mesa2
        mesa1.quitar("Pizza")
        self.assertEqual(mesa1.subtotal(), 0.0)
        self.assertEqual(mesa2.subtotal(), 12000)


class TestCasosLimitePedido(unittest.TestCase):
    """Casos borde relevantes para el pipeline de integración."""

    def test_pedido_vacio_total_es_cero(self):
        menu = Menu()
        menu.agregar_item("Tamal", 7000)
        pedido = Pedido(menu)
        self.assertEqual(pedido.total(), 0.0)

    def test_cantidad_muy_alta_calcula_correctamente(self):
        menu = Menu()
        menu.agregar_item("Tinto", 1000)
        pedido = Pedido(menu)
        pedido.agregar("Tinto", 100)
        self.assertEqual(pedido.subtotal(), 100000)
        self.assertEqual(pedido.total(), round(100000 * 1.19, 2))

    def test_precio_con_decimales_calcula_correctamente(self):
        menu = Menu()
        menu.agregar_item("Jugo natural", 4500.50)
        pedido = Pedido(menu)
        pedido.agregar("Jugo natural", 2)
        self.assertAlmostEqual(pedido.subtotal(), 9001.0, places=2)

    def test_agregar_quitar_y_reagregar_mismo_item(self):
        menu = Menu()
        menu.agregar_item("Caldo", 6000)
        pedido = Pedido(menu)
        pedido.agregar("Caldo", 3)
        pedido.quitar("Caldo")
        pedido.agregar("Caldo", 1)
        self.assertEqual(pedido.resumen()["items"]["caldo"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
