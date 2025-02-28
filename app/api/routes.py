from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.user_service import create_user, get_user_by_email, login_user

router = APIRouter()

@router.post("/registration")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user.email, user.password)

@router.get("/users/{email}")
async def get_user(email: str, db: AsyncSession = Depends(get_db)):
    return await get_user_by_email(db, email)

