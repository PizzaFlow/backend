from datetime import datetime
from typing import List

import pytz
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.order import OrderResponse, OrderCreate, OrderStatusUpdate
from app.services.auth_service import require_employee, require_client
from app.services.order_service import create_order, get_all_orders_for_employee, update_order_status, \
    get_available_delivery_times

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.get("/", dependencies=[Depends(require_employee)], response_model=List[OrderResponse])
async def get_all_current_orders(db: AsyncSession = Depends(get_db)):
    return await get_all_orders_for_employee(db)


@router.patch("/{order_id}/status", dependencies=[Depends(require_employee)], response_model=OrderResponse)
async def change_order_status(order_status_update: OrderStatusUpdate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    return await update_order_status(db, order_status_update.order_id, order_status_update.status, background_tasks)


@router.post("/", response_model=OrderResponse, dependencies=[Depends(require_client)])
async def create_new_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    return await create_order(db, order, user_id, background_tasks)

@router.get("/delivery-times/")
async def get_delivery_times(db: AsyncSession = Depends(get_db)):
    moscow_tz = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(moscow_tz)
    available_times = await get_available_delivery_times(current_time, db)
    return {"delivery_times": available_times}
