# restaurante.py
"""
Sistema de restaurante - SoftNova Demo
Clases: Menu, Pedido
Incluye version() para la etapa BUILD del pipeline.
"""

VERSION = "1.0.0"


def version() -> str:
    return VERSION


class Menu:
    def __init__(self):
        self._items = {}

    def agregar_item(self, nombre: str, precio: float):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del ítem no puede estar vacío.")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a cero.")
        self._items[nombre.lower()] = precio

    def obtener_precio(self, nombre: str) -> float:
        item = self._items.get(nombre.lower())
        if item is None:
            raise KeyError(f"'{nombre}' no está en el menú.")
        return item

    def listar(self) -> dict:
        return dict(self._items)

    def eliminar_item(self, nombre: str):
        if nombre.lower() not in self._items:
            raise KeyError(f"'{nombre}' no está en el menú.")
        del self._items[nombre.lower()]


class Pedido:
    IMPUESTO = 0.19  # 19% IVA Colombia

    def __init__(self, menu: Menu):
        self._menu = menu
        self._items = {}

    def agregar(self, nombre: str, cantidad: int = 1):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        self._menu.obtener_precio(nombre)  # valida existencia
        clave = nombre.lower()
        self._items[clave] = self._items.get(clave, 0) + cantidad

    def quitar(self, nombre: str):
        clave = nombre.lower()
        if clave not in self._items:
            raise KeyError(f"'{nombre}' no está en el pedido.")
        del self._items[clave]

    def subtotal(self) -> float:
        total = 0.0
        for nombre, cantidad in self._items.items():
            total += self._menu.obtener_precio(nombre) * cantidad
        return round(total, 2)

    def impuesto(self) -> float:
        return round(self.subtotal() * self.IMPUESTO, 2)

    def total(self) -> float:
        return round(self.subtotal() + self.impuesto(), 2)

    def resumen(self) -> dict:
        return {
            "items": dict(self._items),
            "subtotal": self.subtotal(),
            "impuesto_19%": self.impuesto(),
            "total": self.total(),
        }
