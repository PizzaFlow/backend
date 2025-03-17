from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.order import DeliveryTimeEnum, PaymentMethodEnum, OrderStatus
from app.schemas.address import AddressResponse
from app.schemas.ingredient import IngredientResponse
from app.schemas.pizza import PizzaResponseForOrder
from app.schemas.user import UserResponseForRegistration


class OrderPizzaIngredientBase(BaseModel):
    ingredient_id: int
    is_added: bool
    count: int


class OrderStatusUpdate(BaseModel):
    order_id: int
    status: OrderStatus


class OrderPizzaIngredientResponse(OrderPizzaIngredientBase):
    ingredient: IngredientResponse

    class Config:
        from_attributes = True


class OrderPizzaBase(BaseModel):
    pizza_id: int
    ingredients: List[OrderPizzaIngredientBase]


class OrderPizzaResponse(BaseModel):
    id: int
    pizza: PizzaResponseForOrder
    custom_price: float
    ingredients: List[OrderPizzaIngredientResponse]

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    address_id: int
    pizzas: List[OrderPizzaBase]
    delivery_time: str
    payment_method: PaymentMethodEnum


class OrderResponse(BaseModel):
    id: int
    user: UserResponseForRegistration
    address: AddressResponse
    status: str
    price: float
    created_at: datetime
    delivery_time: str
    pizzas: List[OrderPizzaResponse]
    payment_method: PaymentMethodEnum

    class Config:
        from_attributes = True