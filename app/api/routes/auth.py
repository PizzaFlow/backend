from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponseForRegistration
from app.services.auth_service import login_user
from app.services.notification_service import send_email, send_email_background
from app.services.user_service import create_user

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=UserResponseForRegistration)
async def register_user(user: UserCreate,
                        role: str = Query(None),
                        db: AsyncSession = Depends(get_db)):
    return await create_user(db, user, role)

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user.email, user.password)