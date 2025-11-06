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
