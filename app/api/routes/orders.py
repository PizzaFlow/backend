from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.order import OrderResponse, OrderCreate, OrderStatusUpdate
from app.services.auth_service import require_employee, require_client
from app.services.order_service import create_order, get_all_orders_for_employee, update_order_status

router = APIRouter()


@router.get("/all-current-orders", dependencies=[Depends(require_employee)], response_model=List[OrderResponse])
async def get_all_current_orders(db: AsyncSession = Depends(get_db)):
    return await get_all_orders_for_employee(db)


@router.patch("/orders/{order_id}", dependencies=[Depends(require_employee)], response_model=OrderResponse)
async def change_order_status(order_status_update: OrderStatusUpdate, db: AsyncSession = Depends(get_db)):
    return await update_order_status(db, order_status_update.order_id, order_status_update.status)


@router.post("/orders/", response_model=OrderResponse, dependencies=[Depends(require_client)])
async def create_new_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client),
):
    user_id = user_data["id"]
    return await create_order(db, order, user_id)
