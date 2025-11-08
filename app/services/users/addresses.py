from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressResponse
from app.utils.geo import reverse_geocode

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


async def add_address(db: AsyncSession, user_id: UUID, data: AddressCreate) -> AddressResponse:
    geo_location = reverse_geocode(data.lat, data.lon)

    if geo_location is None:
        raise Exception()

    new_address = Address(
        user_id=user_id,
        **data.model_dump(),
        **geo_location.model_dump()
    )

    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return AddressResponse.model_validate(new_address)


async def remove_address(db: AsyncSession, user_id: UUID, address_id: UUID) -> None:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()

    if not address:
        raise Exception()
    
    await db.delete(address)
    await db.commit()
