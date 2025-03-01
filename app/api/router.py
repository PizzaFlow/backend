from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.orders import router as orders_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(orders_router)
