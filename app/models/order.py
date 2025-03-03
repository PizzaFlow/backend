from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Изменено на Numeric
    address_id = Column(Integer, ForeignKey("addresses.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    delivery_time = Column(DateTime, nullable=True)  # Изменено на DateTime (или String, если это текст)

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

    order_pizza = relationship("OrderPizza", back_populates="ingredients")
    ingredient = relationship("Ingredient")