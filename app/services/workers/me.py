from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from app.db.session import Session
from app.models.address import Address
from app.models.workers import Worker
from app.schemas.workers import CurrentWorkerResponse, WorkerCreate, WorkerUpdate
from app.services.workers.skills import add_skills
from app.utils.workers import get_worker, get_worker_panic

async def _get_address(db, user_id, address_id):
    stmt = select(Address).where(Address.id == address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_worker(
    db: Session,
    user_id: UUID,
    data: Optional[WorkerCreate]
) -> CurrentWorkerResponse:
    worker = await get_worker(db, user_id,include_deleted=True)

    if worker is not None:
        if worker.deleted_at is not None:
            address = None
            if worker.address_id:
                address = await _get_address(db, user_id, worker.address_id)

            if address is None:
                if data is None or data.address_id is None:
                    raise Exception("Cannot reactivate worker: previous address was removed and no new address was provided.")

                address = await _get_address(db, user_id, data.address_id)
                if address is None:
                    raise Exception("Cannot reactivate worker: provided address does not exist.")

                worker.address_id = address.id

            worker.deleted_at = None

            await db.commit()
            await db.refresh(worker)
            return CurrentWorkerResponse.model_validate(worker)

        raise Exception("Worker already exists.")
        
    if data is None:
        raise Exception("Worker data is required.")

    address = await _get_address(db, user_id, data.address_id)

    if address is None:
        raise Exception("Address not found or does not belong to this user.")

    new_worker = Worker(
        user_id=user_id,
        address_id=address.id,
        bio=data.bio,
        service_radius_km=data.service_radius_km,
        experience_years=data.experience_years,
    )

    db.add(new_worker)
    await db.commit()
    await db.refresh(new_worker)

    if data.skills:
        await add_skills(db, user_id, data.skills, new_worker)
        await db.refresh(new_worker)

    return CurrentWorkerResponse.model_validate(new_worker)


async def get_my_worker_profile(
    db: Session,
    user_id: UUID
) -> CurrentWorkerResponse:
    worker = await get_worker_panic(db, user_id)
    return CurrentWorkerResponse.model_validate(worker)


async def update_worker_profile(
    db: Session,
    user_id: UUID,
    data: WorkerUpdate
) -> CurrentWorkerResponse:
    worker = await get_worker_panic(db, user_id)
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(worker, field, value)

    await db.commit()
    await db.refresh(worker)

    return CurrentWorkerResponse.model_validate(worker)


async def deactivate_worker_profile(
    db: Session,
    user_id: UUID
):
    worker = await get_worker_panic(db, user_id)
    worker.deleted_at = datetime.utcnow()
    await db.commit()
