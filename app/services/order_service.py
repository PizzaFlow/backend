from datetime import datetime, time, timedelta
from typing import List
import pytz

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User, Pizza, Ingredient, Address
from app.models.order import Order, OrderPizza, OrderPizzaIngredient, OrderStatus, DeliveryTimeEnum
from app.schemas.order import OrderCreate, OrderResponse
from app.services.notification_service import send_email_background


async def create_order(db: AsyncSession, order_data: OrderCreate, user_id: int) -> OrderResponse:
    try:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        address = await db.get(Address, order_data.address_id)
        if not address or address.user_id != user_id:
            raise HTTPException(status_code=404, detail="Address not found or does not belong to user")

        total_price = 0.0

        try:
            delivery_time = datetime.strptime(order_data.delivery_time, "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid delivery time format. Please use HH:MM format (e.g., '14:30')."
            )

        moscow_tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(moscow_tz)
        min_delivery_datetime = current_time + timedelta(minutes=30)
        min_delivery_time = min_delivery_datetime.time()

        if delivery_time <= min_delivery_time:
            raise HTTPException(
                status_code=400,
                detail=f"Delivery time must be at least 30 minutes from now. Current time is {current_time.strftime('%H:%M')}, minimum allowed time is {min_delivery_datetime.strftime('%H:%M')}."
            )

        allowed_delivery_times = [enum_value.value for enum_value in DeliveryTimeEnum]
        if delivery_time not in allowed_delivery_times:
            allowed_times_str = ", ".join([t.strftime("%H:%M") for t in allowed_delivery_times])
            raise HTTPException(
                status_code=400,
                detail=f"Delivery time must be one of the following: {allowed_times_str}."
            )

        new_order = Order(
            user_id=user_id,
            address_id=order_data.address_id,
            status=OrderStatus.CREATED,
            price=0.0,
            delivery_time=delivery_time,
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
        order.delivery_time = order.delivery_time.strftime("%H:%M")
        return OrderResponse.from_orm(order)

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_available_delivery_times(current_time: datetime, db: AsyncSession) -> List[str]:
    start_time = time(9, 0)
    end_time = time(22, 0)
    interval = 30

    delivery_times = []
    current_slot = datetime.combine(datetime.today(), start_time)
    end_slot = datetime.combine(datetime.today(), end_time)

    while current_slot.time() < current_time.time():
        current_slot += timedelta(minutes=interval)

    current_slot += timedelta(minutes=interval)

    while current_slot <= end_slot:
        next_slot = current_slot + timedelta(minutes=interval)
        delivery_times.append(
            f"{current_slot.strftime('%H:%M')}-{next_slot.strftime('%H:%M')}"
        )
        current_slot = next_slot

    active_orders = await get_all_orders_for_employee(db)
    active_orders_count = len(active_orders)

    slots_to_remove = 0
    if active_orders_count >= 15:
        slots_to_remove = 3
    elif active_orders_count >= 10:
        slots_to_remove = 2
    elif active_orders_count >= 5:
        slots_to_remove = 1

    if slots_to_remove > 0 and len(delivery_times) > slots_to_remove:
        delivery_times = delivery_times[slots_to_remove:]
    elif slots_to_remove >= len(delivery_times):
        return []

    return delivery_times
async def update_order_status(db: AsyncSession, order_id: int, new_status: OrderStatus, background_tasks: BackgroundTasks,) -> OrderResponse:
    try:
        order = await db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")

        order.status = new_status
        await db.flush()

        await db.commit()

        await db.refresh(order)

        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.address),
                selectinload(Order.pizzas).selectinload(OrderPizza.pizza).selectinload(Pizza.ingredients),
                selectinload(Order.pizzas).selectinload(OrderPizza.ingredients).selectinload(
                    OrderPizzaIngredient.ingredient)
            )
        )

        updated_order = result.scalars().first()


        if background_tasks:
            user = order.user
            subject = f"Обновлен статус заказа № {order_id}"
            body = f"Статус вашего заказа: {order_id} сменился на {new_status.value}"
            send_email_background(background_tasks, user.email, subject, body)
        return OrderResponse.from_orm(updated_order)

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")


async def get_all_orders_for_employee(db: AsyncSession) -> List[OrderResponse]:
    try:
        result = await db.execute(
            select(Order)
            .where(Order.status != OrderStatus.COMPLETED)
            .options(
                selectinload(Order.user),
                selectinload(Order.address),
                selectinload(Order.pizzas).selectinload(OrderPizza.pizza).selectinload(Pizza.ingredients),
                selectinload(Order.pizzas).selectinload(OrderPizza.ingredients).selectinload(
                    OrderPizzaIngredient.ingredient)
            )
            .order_by(Order.id)
        )

        orders = result.scalars().all()

        for order in orders:
            if order.delivery_time:
                order.delivery_time = order.delivery_time.strftime("%H:%M")

        return [OrderResponse.from_orm(order) for order in orders]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


async def get_all_orders(db: AsyncSession, user_id: int) -> List[OrderResponse]:
    try:
        result = await db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.user),
                selectinload(Order.address),
                selectinload(Order.pizzas).selectinload(OrderPizza.pizza).selectinload(Pizza.ingredients),
                selectinload(Order.pizzas).selectinload(OrderPizza.ingredients).selectinload(
                    OrderPizzaIngredient.ingredient)
            )
            .order_by(Order.id)
        )

        orders = result.scalars().all()

        for order in orders:
            if order.delivery_time:
                order.delivery_time = order.delivery_time.strftime("%H:%M")

        return [OrderResponse.from_orm(order) for order in orders]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")
