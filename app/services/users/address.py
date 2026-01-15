from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate
from app.utils.geo import reverse_geocode
from app.utils.workers import get_worker

async def get_all_addresses(db: AsyncSession, user_id: UUID) -> List[AddressResponse]:
    result = await db.execute(select(Address).where(Address.user_id == user_id))
    addresses = result.scalars().all()
    return [AddressResponse.model_validate(addr) for addr in addresses]


async def get_addresses_by_id(db: AsyncSession, user_id: UUID, address_id: UUID) -> AddressResponse:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()

    if not address:
        raise HTTPException(404, "Address not found")

    return AddressResponse.model_validate(address)


async def add_address(db: AsyncSession, user_id: UUID, data: AddressCreate) -> AddressResponse:
    geo_location = reverse_geocode(data.lat, data.lon)

    if geo_location is None:
        raise HTTPException(500, "Can not get geo location")

    new_address = Address(
        user_id=user_id,
        **data.model_dump(),
        **geo_location.model_dump()
    )

    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return AddressResponse.model_validate(new_address)


async def update_address(db: AsyncSession, user_id: UUID, address_id: UUID, data: AddressUpdate) -> AddressResponse:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()

    if not address:
        raise HTTPException(404, "Address not found")
    
    location_available = data.lon is not None and data.lat is not None
    location_change = data.lon != address.lon or data.lat != address.lat

    if location_available and location_change:
        geo_location = reverse_geocode(data.lat, data.lon)
        for field, value in geo_location.model_dump(exclude_none=True).items():
            setattr(address, field, value)
        address.lon = data.lon
        address.lat = data.lat

    if data.label is not None:
        address.label = data.label

    await db.commit()
    await db.refresh(address)
    return AddressResponse.model_validate(address)


async def remove_address(db: AsyncSession, user_id: UUID, address_id: UUID) -> None:
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()

    if not address:
        raise HTTPException(404, "Address not found")
    
    worker = await get_worker(db, user_id)
    if worker and not worker.deleted_at:
        if worker.address_id == address.id:
            raise HTTPException(409, "Address is currently assigned to a worker")

    
    await db.delete(address)
    await db.commit()
