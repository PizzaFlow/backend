from typing import Optional

from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    price: float


class IngredientResponse(IngredientBase):
    id: int
    photo: Optional[str] = None

    class Config:
        from_attributes = True
