from typing import List

from fastapi import HTTPException
from sqlalchemy import select, insert, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import user_pizza_association
from app.models.pizza import Pizza


async def get_all_pizzas_with_ingredients(db: AsyncSession) -> List[Pizza]:
    result = await db.execute(
        select(Pizza).options(selectinload(Pizza.ingredients))
    )
    return result.scalars().all()


async def get_favorite_pizzas(db: AsyncSession, user_id: int) -> List[Pizza]:
    result = await db.execute(
        select(Pizza)
        .join(user_pizza_association)
        .filter(user_pizza_association.c.user_id == user_id)
        .options(selectinload(Pizza.liked_by_users))
        .options(selectinload(Pizza.ingredients))
    )
    return result.scalars().all()


async def add_favorite_pizza(db: AsyncSession, user_id: int, pizza_id: int) -> None:
    check_stmt = select(user_pizza_association).where(
        user_pizza_association.c.user_id == user_id,
        user_pizza_association.c.pizza_id == pizza_id
    )
    result = await db.execute(check_stmt)
    existing_record = result.scalar_one_or_none()

    if existing_record:
        raise HTTPException(status_code=409, detail="This pizza is already in user's favorites")

    try:
        stmt = insert(user_pizza_association).values(user_id=user_id, pizza_id=pizza_id)
        await db.execute(stmt)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="This pizza is already in user's favorites")


async def delete_favorite_pizza(db: AsyncSession, user_id: int, pizza_id: int) -> None:
    check_stmt = select(user_pizza_association).where(
        user_pizza_association.c.user_id == user_id,
        user_pizza_association.c.pizza_id == pizza_id
    )
    result = await db.execute(check_stmt)
    existing_record = result.scalar_one_or_none()

    if not existing_record:
        raise HTTPException(status_code=404, detail="This pizza is not in user's favorites")

    stmt = delete(user_pizza_association).where(
        user_pizza_association.c.user_id == user_id,
        user_pizza_association.c.pizza_id == pizza_id
    )
    await db.execute(stmt)
    await db.commit()
