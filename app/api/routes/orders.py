from typing import List

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.order import OrderResponse, OrderCreate
from app.schemas.user import PizzaResponse
from app.services.auth_service import require_employee, verify_token, http_bearer
from app.services.order_service import create_order
from app.services.pizza_service import get_all_pizzas_with_ingredients

router = APIRouter()

@router.get("/all-current-orders", dependencies=[Depends(require_employee)])
async def get_all_current_orders(db: AsyncSession = Depends(get_db)):
    return 0

@router.post("/orders/", response_model=OrderResponse)
async def create_new_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
):
    user_data = verify_token(credentials)
    user_id = user_data["id"]

    # Передаем user_id в метод create_order
    return await create_order(db, order, user_id)

@router.get("/pizzas", response_model=List[PizzaResponse])
async def get_pizzas(db: AsyncSession = Depends(get_db)):
    pizzas = await get_all_pizzas_with_ingredients(db)
    return pizzas