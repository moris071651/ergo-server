from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.models import Address
from app.schemas.address import AddressResponse

async def get_all_addresses(db: AsyncSession, user_id: UUID) -> List[AddressResponse]:
    result = await db.execute(select(Address).where(Address.user_id == user_id))
    addresses = result.scalars().all()
    return [AddressResponse.model_validate(addr) for addr in addresses]


async def get_addresses_by_id(db: AsyncSession, user_id: UUID, address_id: UUID) -> AddressResponse:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()

    if not address:
        raise Exception()

    return AddressResponse.model_validate(address)


async def remove_address(db: AsyncSession, user_id: UUID, address_id: UUID) -> None:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()

    if not address:
        raise Exception()
    
    await db.delete(address)
    await db.commit()
