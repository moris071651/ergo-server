from datetime import datetime
from typing import Optional
from uuid import UUID
from app.db.session import Session
from app.models.workers import Worker
from app.schemas.workers import CurrentWorkerResponse, WorkerCreate, WorkerUpdate
from app.services.workers.skills import add_skills
from app.utils.workers import get_worker, get_worker_panic


async def create_worker(
    db: Session,
    user_id: UUID,
    data: Optional[WorkerCreate]
) -> CurrentWorkerResponse:
    worker = await get_worker(db, user_id, True)
    if worker is not None:
        if worker.deleted_at is not None:
            worker.deleted_at = None
            await db.commit()
            await db.refresh(worker)
            return CurrentWorkerResponse.model_validate(worker)
        
        else:
            raise Exception()
        
    if data is None:
        raise Exception()

    new_worker = Worker(
        user_id=user_id,
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
