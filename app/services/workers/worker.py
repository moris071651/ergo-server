from typing import List
from uuid import UUID

from sqlalchemy import select
from app.db.session import Session
from app.models.workers import Worker
from app.schemas.workers import WorkerResponse
from app.utils.workers import get_worker_panic


async def get_worker_profile(
    db: Session,
    user_id: UUID
) -> WorkerResponse:
    worker = await get_worker_panic(db, user_id)
    return WorkerResponse.model_validate(worker)


async def get_all_worker_profiles(
    db: Session
) -> List[WorkerResponse]:
    stmt = select(Worker).where(Worker.deleted_at == None)
    result = await db.execute(stmt)
    workers = result.scalars().all()   
    return [WorkerResponse.model_validate(worker) for worker in workers]
