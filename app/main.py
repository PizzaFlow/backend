from fastapi import FastAPI
from app.api.router import router
from app.core.database import init_db, get_db, get_db_sync
from sqlalchemy.future import select
from sqlalchemy import text

from app.models import Pizza, Ingredient, PizzaIngredient

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_db()

    # Просто вызываем get_db_sync() как корутину, а не с async with
    db = await get_db_sync()  # Получаем сессию

    # Применяем SQL-скрипты, если необходимо
    result = await db.execute(select(Pizza.id).limit(1))
    pizza_id = result.scalars().first()
    if not pizza_id:
        with open("./app/sql_scripts/init_pizzas.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()
            await db.execute(text(sql_script))
            await db.commit()
        print("Инициализированы данные для таблицы pizza")

    result = await db.execute(select(Ingredient.id).limit(1))
    ingredient_id = result.scalars().first()
    if not ingredient_id:
        with open("./app/sql_scripts/init_ingredients.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()
            await db.execute(text(sql_script))
            await db.commit()
        print("Инициализированы данные для таблицы ingredients")

    result = await db.execute(select(PizzaIngredient.pizza_id).limit(1))
    pizza_ingredient_id = result.scalars().first()
    if not pizza_ingredient_id:
        with open("./app/sql_scripts/pizza_ingredient.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()
            await db.execute(text(sql_script))
            await db.commit()
        print("Инициализированы данные для таблицы pizza_ingredients")

app.include_router(router)