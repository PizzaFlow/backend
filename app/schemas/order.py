# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.user import UserResponse, AddressResponse, IngredientResponse, PizzaResponse

# Кастомизация ингредиентов в пицце заказа
class OrderPizzaIngredientBase(BaseModel):
    ingredient_id: int
    is_added: bool

class OrderPizzaIngredientResponse(OrderPizzaIngredientBase):
    ingredient: IngredientResponse

    class Config:
        from_attributes = True

# Пицца в заказе (запрос — только ID и ингредиенты)
class OrderPizzaBase(BaseModel):
    pizza_id: int
    ingredients: List[OrderPizzaIngredientBase]

# Пицца в заказе (ответ — с рассчитанной ценой)
class OrderPizzaResponse(BaseModel):
    id: int
    pizza: PizzaResponse
    custom_price: float
    ingredients: List[OrderPizzaIngredientResponse]

    class Config:
        from_attributes = True

# Создание заказа (запрос — без status и user_id)
class OrderCreate(BaseModel):
    address_id: int
    pizzas: List[OrderPizzaBase]

# Ответ с деталями заказа
class OrderResponse(BaseModel):
    id: int
    user: UserResponse
    address: AddressResponse
    status: str
    price: float
    created_at: datetime
    delivery_time: Optional[datetime] = None
    pizzas: List[OrderPizzaResponse]

    class Config:
        from_attributes = True