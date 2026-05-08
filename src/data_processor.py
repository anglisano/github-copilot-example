from pydantic import BaseModel
from typing import List

# This file serves to test the project instructions (.github/copilot-instructions.md)
# The instructions say: Use Pydantic, Type Hints, English, and Functional Programming.

class Sale(BaseModel):
    id: int
    product: str
    price: float
    quantity: int

def process_total_sales(sales: List[Sale]) -> float:
    """
    Calculates the total of all sales in a functional way.
    """
    return sum(map(lambda s: s.price * s.quantity, sales))

# Example data for testing
if __name__ == "__main__":
    data = [
        Sale(id=1, product="Keyboard", price=50.0, quantity=2),
        Sale(id=2, product="Mouse", price=25.0, quantity=1)
    ]
    print(f"Total processed: {process_total_sales(data)}")
