from sqlalchemy import Column, Integer, String, ForeignKey, Numeric

from app.core.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    photo = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)

class PizzaIngredient(Base):
    __tablename__ = "pizza_ingredients"

    pizza_id = Column(Integer, ForeignKey("pizzas.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)