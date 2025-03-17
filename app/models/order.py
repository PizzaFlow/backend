import datetime
import enum

from sqlalchemy import Boolean
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Enum as SQLEnum, Time
from sqlalchemy.orm import relationship

from app.core.database import Base


class DeliveryTimeEnum(enum.Enum):
    T_09_00 = datetime.time(9, 0)
    T_09_30 = datetime.time(9, 30)
    T_10_00 = datetime.time(10, 0)
    T_10_30 = datetime.time(10, 30)
    T_11_00 = datetime.time(11, 0)
    T_11_30 = datetime.time(11, 30)
    T_12_00 = datetime.time(12, 0)
    T_12_30 = datetime.time(12, 30)
    T_13_00 = datetime.time(13, 0)
    T_13_30 = datetime.time(13, 30)
    T_14_00 = datetime.time(14, 0)
    T_14_30 = datetime.time(14, 30)
    T_15_00 = datetime.time(15, 0)
    T_15_30 = datetime.time(15, 30)
    T_16_00 = datetime.time(16, 0)
    T_16_30 = datetime.time(16, 30)
    T_17_00 = datetime.time(17, 0)
    T_17_30 = datetime.time(17, 30)
    T_18_00 = datetime.time(18, 0)
    T_18_30 = datetime.time(18, 30)
    T_19_00 = datetime.time(19, 0)
    T_19_30 = datetime.time(19, 30)
    T_20_00 = datetime.time(20, 0)
    T_20_30 = datetime.time(20, 30)
    T_21_00 = datetime.time(21, 0)
    T_21_30 = datetime.time(21, 30)
    T_22_00 = datetime.time(22, 0)


class PaymentMethodEnum(str, enum.Enum):
    CARD_ON_DELIVERY = "Картой при получении"
    CASH_ON_DELIVERY = "Наличными при получении"


class OrderStatus(str, enum.Enum):
    CREATED = "Создан"
    COOKING = "Готовится"
    DELIVERY = "Доставляется"
    COMPLETED = "Завершен"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(SQLEnum(OrderStatus), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    delivery_time = Column(Time, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethodEnum), nullable=False)

    user = relationship("User", back_populates="orders")
    address = relationship("Address", back_populates="order", uselist=False)
    pizzas = relationship("OrderPizza", back_populates="order")
class OrderPizza(Base):
    __tablename__ = "order_pizzas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    pizza_id = Column(Integer, ForeignKey("pizzas.id"), nullable=False)
    custom_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="pizzas")
    pizza = relationship("Pizza")
    ingredients = relationship("OrderPizzaIngredient", back_populates="order_pizza")
class OrderPizzaIngredient(Base):
    __tablename__ = "order_pizza_ingredients"

    order_pizza_id = Column(Integer, ForeignKey("order_pizzas.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    is_added = Column(Boolean, nullable=False)
    count = Column(Integer, nullable=False)

    order_pizza = relationship("OrderPizza", back_populates="ingredients")
    ingredient = relationship("Ingredient")