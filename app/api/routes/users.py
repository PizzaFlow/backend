from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.address import AddressBase, AddressResponse
from app.schemas.order import OrderResponse
from app.schemas.pizza import PizzaResponse
from app.services.address_service import added_new_address, get_all_addresses, remove_address
from app.services.auth_service import require_client
from app.services.order_service import get_all_orders
from app.services.pizza_service import get_favorite_pizzas, add_favorite_pizza, delete_favorite_pizza
from app.services.user_service import get_user_by_id

router = APIRouter()


@router.get("/users/", dependencies=[Depends(require_client)])
async def get_user(db: AsyncSession = Depends(get_db),
                   user_data: dict = Depends(require_client)):
    user_id = user_data["id"]
    return await get_user_by_id(db, user_id)


@router.post("/users/address/", dependencies=[Depends(require_client)])
async def added_address(
        address: AddressBase,
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    return await added_new_address(db, address, user_id)


@router.get("/users/address/", dependencies=[Depends(require_client)], response_model=List[AddressResponse])
async def get_address(
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    return await get_all_addresses(db, user_id)


@router.delete("/users/address/{address_id}", dependencies=[Depends(require_client)])
async def delete_address(
        address_id: int,
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client),
):
    user_id = user_data["id"]
    await remove_address(db, address_id, user_id)
    return {"message": "Address deleted successfully"}


@router.get("/users/orders/", dependencies=[Depends(require_client)], response_model=List[OrderResponse])
async def get_orders(
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    return await get_all_orders(db, user_id)


@router.get("/users/pizzas/", dependencies=[Depends(require_client)], response_model=List[PizzaResponse])
async def get_likes_pizzas(
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    return await get_favorite_pizzas(db, user_id)


@router.post("/users/pizzas/{pizza_id}", dependencies=[Depends(require_client)])
async def add_pizza_in_favorite(
        pizza_id: int,
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    await add_favorite_pizza(db, user_id, pizza_id)
    return {"message: pizza with id: " + str(pizza_id) + " was successfully added"}


@router.delete("/users/pizzas/{pizza_id}", dependencies=[Depends(require_client)])
async def delete_pizza_in_favorite(
        pizza_id: int,
        db: AsyncSession = Depends(get_db),
        user_data: dict = Depends(require_client)
):
    user_id = user_data["id"]
    await delete_favorite_pizza(db, user_id, pizza_id)
    return {"message: pizza with id: " + str(pizza_id) + " was successfully deleted from favorite pizzas"}
