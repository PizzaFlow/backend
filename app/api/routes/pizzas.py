from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.ingredient import IngredientResponse
from app.schemas.pizza import PizzaResponse
from app.services.pizza_service import get_all_pizzas_with_ingredients, get_all_ingredients

router = APIRouter(
    tags=["Пиццы и ингредиенты"]
)


@router.get("/pizzas", response_model=List[PizzaResponse])
async def get_pizzas(db: AsyncSession = Depends(get_db)):
    pizzas = await get_all_pizzas_with_ingredients(db)
    return pizzas

@router.get("/ingredients", response_model=List[IngredientResponse])
async def get_ingredients(db: AsyncSession = Depends(get_db)):
    ingredients = await get_all_ingredients(db)
    return ingredients