from typing import List, Optional

from pydantic import BaseModel

from app.schemas.ingredient import IngredientResponse


class PizzaBase(BaseModel):
    name: str
    price: float
    description: str


class PizzaResponse(PizzaBase):
    id: int
    ingredients: List[IngredientResponse]
    photo: Optional[str] = None

    class Config:
        from_attributes = True

class PizzaResponseForOrder(PizzaBase):
    id: int
    photo: str

    class Config:
        from_attributes = True
