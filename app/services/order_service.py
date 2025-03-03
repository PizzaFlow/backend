from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User, Pizza, Ingredient, Address
from app.models.order import Order, OrderPizza, OrderPizzaIngredient
from app.schemas.order import OrderCreate, OrderResponse


async def create_order(db: AsyncSession, order_data: OrderCreate, user_id: int) -> OrderResponse:
    try:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        address = await db.get(Address, order_data.address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=404, detail="Address not found or does not belong to user")

        total_price = 0.0

        new_order = Order(
            user_id=user_id,
            address_id=order_data.address_id,
            status="created",
            price=0.0,
            delivery_time=order_data.delivery_time,
            payment_method=order_data.payment_method
        )
        db.add(new_order)
        await db.flush()

        for pizza_data in order_data.pizzas:

            pizza = await db.get(Pizza, pizza_data.pizza_id)
            if not pizza:
                raise HTTPException(status_code=404, detail=f"Pizza with id {pizza_data.pizza_id} not found")

            custom_price = float(pizza.price)
            for ingredient_data in pizza_data.ingredients:
                ingredient = await db.get(Ingredient, ingredient_data.ingredient_id)
                if not ingredient:
                    raise HTTPException(status_code=404,
                                        detail=f"Ingredient with id {ingredient_data.ingredient_id} not found")
                if ingredient_data.is_added:
                    if (ingredient_data.count == 0):
                        ingredient_data.count = 1
                    custom_price += float(ingredient.price) * ingredient_data.count

            order_pizza = OrderPizza(
                order_id=new_order.id,
                pizza_id=pizza_data.pizza_id,
                custom_price=custom_price
            )
            db.add(order_pizza)
            await db.flush()

            for ingredient_data in pizza_data.ingredients:
                order_pizza_ingredient = OrderPizzaIngredient(
                    order_pizza_id=order_pizza.id,
                    ingredient_id=ingredient_data.ingredient_id,
                    is_added=ingredient_data.is_added,
                    count=ingredient_data.count
                )
                db.add(order_pizza_ingredient)

            total_price += custom_price

        new_order.price = total_price
        await db.flush()

        await db.commit()

        await db.refresh(new_order)

        result = await db.execute(
            select(Order)
            .where(Order.id == new_order.id)
            .options(
                selectinload(Order.user),
                selectinload(Order.address),
                selectinload(Order.pizzas).selectinload(OrderPizza.pizza).selectinload(Pizza.ingredients),
                selectinload(Order.pizzas).selectinload(OrderPizza.ingredients).selectinload(
                    OrderPizzaIngredient.ingredient)
            )
        )
        order = result.scalars().first()
        return OrderResponse.from_orm(order)

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))