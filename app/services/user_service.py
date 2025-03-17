from fastapi import HTTPException, BackgroundTasks
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserCreate, UserEditSchema, UserResponseForRegistration, UserResponse
from app.services.notification_service import send_email_background

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


async def create_user(db: AsyncSession, user: UserCreate, role: str):
    existing_user = await db.execute(
        select(User).filter((User.email == user.email))
    )
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Пользователь с таким email или username уже существует")

    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="CLIENT"
    )

    if role == "EMPLOYEE":
        db_user.role = "EMPLOYEE"

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return UserResponseForRegistration.from_orm(db_user)


async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, id: int):
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == id))
        return UserResponse.from_orm(result.scalar_one_or_none())

async def path_edit_user(db: AsyncSession, user_data: UserEditSchema, id: int):
    stmt = select(User).where(User.id == id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.username:
        user.username = user_data.username
    if user_data.phone_number:
        user.phone_number = user_data.phone_number
    if user_data.password:
        user.hashed_password = pwd_context.hash(user_data.password)

    await db.commit()

    result = await db.execute(select(User).filter(User.id == id))

    return UserResponse.from_orm(result.scalar_one_or_none())