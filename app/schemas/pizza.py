from typing import List

from pydantic import BaseModel

from app.schemas.ingredient import IngredientResponse


class PizzaBase(BaseModel):
    name: str
    price: float
    description: str


class PizzaResponse(PizzaBase):
    id: int
    ingredients: List[IngredientResponse]

    class Config:
        from_attributes = True

class PizzaResponseForOrder(PizzaBase):
    id: int

    class Config:
        from_attributes = True
