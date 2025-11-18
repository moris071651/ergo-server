from typing import Optional
from uuid import UUID
from sqlalchemy import select

from app.db.session import Session
from app.models.workers import Worker


async def get_worker(db: Session, user_id: UUID) -> Optional[Worker]:
    stmt = select(Worker).where(Worker.user_id == user_id)
    result = await db.execute(stmt)
    worker = result.scalars().first()    
    return worker


async def get_worker_panic(db: Session, user_id: UUID) -> Worker:
    worker = await get_worker(db, user_id)

    if not worker:
        raise Exception("Worker not found")
    
    return worker
