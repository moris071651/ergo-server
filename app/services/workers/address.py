from uuid import UUID
from sqlalchemy import select
from app.db.session import Session
from app.models.address import Address
from app.schemas.address import AddressResponse, PublicAddressResponse, MainAddressUpdate
from app.utils.workers import get_worker_panic


async def _get_address(db, user_id, res_type):
    worker = await get_worker_panic(db, user_id)
    if worker.address is None:
        raise Exception('Internal Server Error')
    
    return res_type.model_validate(worker.address)


async def get_my_main_address(
    db: Session,
    user_id: UUID
) -> AddressResponse:
    return await _get_address(db, user_id, AddressResponse)   


async def update_my_main_address(
    db: Session,
    user_id: UUID,
    data: MainAddressUpdate
) -> AddressResponse:
    worker = await get_worker_panic(db, user_id)

    if data.address_id == worker.address_id:
        raise Exception("This address is already your main address.")
    
    stmt = select(Address).where(
        Address.id == data.address_id,
        Address.user_id == user_id
    )
    result = await db.execute(stmt)
    new_addr = result.scalars().first()

    if new_addr is None:
        raise Exception("Address not found or does not belong to this user.")
    
    worker.address_id = new_addr.id

    await db.commit()
    await db.refresh(worker)

    return AddressResponse.model_validate(worker.address)


async def get_worker_main_address(
    db: Session,
    user_id: UUID
) -> PublicAddressResponse:
    return await _get_address(db, user_id, PublicAddressResponse)   
