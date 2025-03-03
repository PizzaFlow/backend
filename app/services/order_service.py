# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models import User, Pizza, Ingredient, Address
from app.models.order import Order, OrderPizza, OrderPizzaIngredient
from app.schemas.order import OrderCreate, OrderResponse
from fastapi import HTTPException

async def create_order(db: AsyncSession, order_data: OrderCreate, user_id: int) -> OrderResponse:
    try:
        # Проверяем существование пользователя и адреса
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        address = await db.get(Address, order_data.address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=404, detail="Address not found or does not belong to user")

        total_price = 0.0  # Итоговая стоимость заказа

        # Создаём заказ
        new_order = Order(
            user_id=user_id,
            address_id=order_data.address_id,
            status="created",  # Автоматически "created"
            price=0.0  # Временно, обновим позже
        )
        db.add(new_order)
        await db.flush()  # Сохраняем заказ, чтобы получить его ID

        # Создаём пиццы в заказе
        for pizza_data in order_data.pizzas:
            # Проверяем существование пиццы
            pizza = await db.get(Pizza, pizza_data.pizza_id)
            if not pizza:
                raise HTTPException(status_code=404, detail=f"Pizza with id {pizza_data.pizza_id} not found")

            # Рассчитываем цену: базовая цена пиццы + стоимость добавленных ингредиентов
            custom_price = float(pizza.price)  # Базовая цена из таблицы pizzas
            for ingredient_data in pizza_data.ingredients:
                ingredient = await db.get(Ingredient, ingredient_data.ingredient_id)
                if not ingredient:
                    raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_data.ingredient_id} not found")
                if ingredient_data.is_added:  # Добавляем стоимость только для новых ингредиентов
                    custom_price += float(ingredient.price)

            order_pizza = OrderPizza(
                order_id=new_order.id,
                pizza_id=pizza_data.pizza_id,
                custom_price=custom_price
            )
            db.add(order_pizza)
            await db.flush()  # Сохраняем пиццу, чтобы получить её ID

            # Создаём кастомные ингредиенты
            for ingredient_data in pizza_data.ingredients:
                order_pizza_ingredient = OrderPizzaIngredient(
                    order_pizza_id=order_pizza.id,
                    ingredient_id=ingredient_data.ingredient_id,
                    is_added=ingredient_data.is_added
                )
                db.add(order_pizza_ingredient)

            total_price += custom_price  # Добавляем к общей стоимости

        # Обновляем итоговую цену заказа
        new_order.price = total_price
        await db.flush()

        # Коммитим транзакцию
        await db.commit()

        # Обновляем объект заказа, чтобы он содержал все связанные данные
        await db.refresh(new_order)

        # Получаем полный объект заказа с зависимостями
        result = await db.execute(
            select(Order)
            .where(Order.id == new_order.id)
            .options(
                selectinload(Order.user),
                selectinload(Order.address),
                selectinload(Order.pizzas).selectinload(OrderPizza.pizza),
                selectinload(Order.pizzas).selectinload(OrderPizza.ingredients).selectinload(OrderPizzaIngredient.ingredient)
            )
        )
        order = result.scalars().first()
        return OrderResponse.from_orm(order)

    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))