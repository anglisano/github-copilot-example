---
name: pydantic-validator
description: Generate Pydantic BaseModel classes with type hints and pytest tests. Use when asked to validate a data structure, create a model, or add validation to a dict or JSON.
---


# Pydantic Validator Skill

## When to Use
- User asks to "validate this structure" or "create a model for..."
- Need to add data validation to a dict, JSON payload, or raw input
- User wants to refactor a plain dict/class into a typed model

## Procedure
1. Analyze the fields of the provided dict, JSON, or class
2. Generate a class inheriting from `pydantic.BaseModel` with full type hints
3. Add a custom `@field_validator` for date fields (ISO format) or price/currency fields (must be > 0)
4. Create a `pytest` test in `src/` that covers:
   - A valid input that should pass
   - An invalid input that should raise `ValidationError`

## Example Output Shape
```python
from pydantic import BaseModel, field_validator
from typing import Optional

class ProductSale(BaseModel):
    product: str
    price: float
    quantity: int

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be positive")
        return v