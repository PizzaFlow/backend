from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import require_client
from app.services.user_service import get_user_by_email, get_user_by_id

router = APIRouter()

@router.get("/users/{email}", dependencies=[Depends(require_client)])
async def get_user(email: str, db: AsyncSession = Depends(get_db)):
    return await get_user_by_email(db, email)

@router.get("/users/{id}", dependencies=[Depends(require_client)])
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_by_id(db, id)