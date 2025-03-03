# app/crud.py (дополнение)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.pizza import Pizza
from app.schemas.user import PizzaResponse
from typing import List

async def get_all_pizzas_with_ingredients(db: AsyncSession) -> List[Pizza]:
    result = await db.execute(
        select(Pizza).options(selectinload(Pizza.ingredients))
    )
    return result.scalars().all()