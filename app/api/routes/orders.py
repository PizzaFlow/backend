from fastapi import APIRouter, Depends
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import require_employee

router = APIRouter()

@router.get("/all-current-orders", dependencies=[Depends(require_employee)])
async def get_all_current_orders(db: AsyncSession = Depends(get_db)):
    return 0