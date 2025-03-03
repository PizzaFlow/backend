from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str
    price: float


class IngredientResponse(IngredientBase):
    id: int

    class Config:
        from_attributes = True
