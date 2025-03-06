from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.pizza import PizzaResponse
from app.services.pizza_service import get_all_pizzas_with_ingredients

router = APIRouter(
    prefix="/pizzas",
    tags=["Пиццы"]
)


@router.get("/", response_model=List[PizzaResponse])
async def get_pizzas(db: AsyncSession = Depends(get_db)):
    pizzas = await get_all_pizzas_with_ingredients(db)
    return pizzas