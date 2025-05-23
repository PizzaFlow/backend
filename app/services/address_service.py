from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Address
from app.schemas.address import AddressBase, AddressResponse


async def added_new_address(db: AsyncSession, address: AddressBase, user_id: int) -> AddressResponse:
    db_address = Address(
        user_id=user_id,
        city=address.city,
        street=address.street,
        house=address.house,
        apartment=address.apartment
    )
    db.add(db_address)
    await db.commit()
    await db.refresh(db_address)
    return db_address

async def get_all_addresses(db: AsyncSession, user_id: int) -> List[AddressResponse]:
    async with db.begin():
        stmt = select(Address).where(Address.user_id == user_id)
        result = await db.execute(stmt)
        addresses = result.scalars().all()
        return [AddressResponse.from_orm(address) for address in addresses]

async def remove_address(db: AsyncSession, address_id: int, user_id: int):
    async with db.begin():
        stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
        result = await db.execute(stmt)
        address = result.scalars().first()
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        await db.delete(address)

async def get_address_by_id(db: AsyncSession, pizza_id: int) -> AddressResponse:
    async with db.begin():
        stmt = select(Address).where(Address.id == pizza_id)
        result = await db.execute(stmt)
        address = result.scalars().one_or_none()
        return AddressResponse.from_orm(address)