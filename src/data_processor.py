from pydantic import BaseModel
from typing import List

# Este archivo sirve para probar las instrucciones de proyecto (.github/copilot-instructions.md)
# Las instrucciones dicen: Usar Pydantic, Type Hints, Español y Programación Funcional.

class Venta(BaseModel):
    id: int
    producto: str
    precio: float
    cantidad: int

def procesar_ventas_totales(ventas: List[Venta]) -> float:
    """
    Calcula el total de todas las ventas de forma funcional.
    """
    return sum(map(lambda v: v.precio * v.cantidad, ventas))

# Ejemplo de datos para probar
if __name__ == "__main__":
    datos = [
        Venta(id=1, producto="Teclado", precio=50.0, cantidad=2),
        Venta(id=2, producto="Ratón", precio=25.0, cantidad=1)
    ]
    print(f"Total procesado: {procesar_ventas_totales(datos)}")
