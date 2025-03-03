from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import user_pizza_association

class Pizza(Base):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # Добавлено unique=True
    price = Column(Numeric(10, 2), nullable=False)  # Изменено на Numeric
    description = Column(String, nullable=False)

    liked_by_users = relationship("User", secondary=user_pizza_association, back_populates="favorite_pizzas")
    ingredients = relationship("Ingredient", secondary="pizza_ingredients")