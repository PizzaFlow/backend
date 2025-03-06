from fastapi import HTTPException, BackgroundTasks
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.notification_service import send_email_background

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


async def create_user(db: AsyncSession, user: UserCreate, role: str):
    existing_user = await db.execute(
        select(User).filter((User.email == user.email) | (User.username == user.username))
    )
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Пользователь с таким email или username уже существует")

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role="CLIENT"
    )

    if role == "EMPLOYEE":
        db_user.role = "EMPLOYEE"

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, id: int):
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == 1))
        return result.scalar_one_or_none()
