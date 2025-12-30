from typing import Optional
from uuid import UUID
from sqlalchemy import exists, select

from app.db.session import Session
from app.models.workers import Worker


async def get_worker(db: Session, user_id: UUID, include_deleted: bool = False) -> Optional[Worker]:
    stmt = select(Worker).where(Worker.user_id == user_id and Worker.deleted_at == None)
    
    if include_deleted == True:
        stmt = stmt.where(Worker.user_id == user_id)

    else:
        stmt = stmt.where(Worker.user_id == user_id and Worker.deleted_at == None)

    result = await db.execute(stmt)
    worker = result.scalars().first()    
    return worker


async def get_worker_panic(db: Session, user_id: UUID, include_deleted: bool = False) -> Worker:
    worker = await get_worker(db, user_id, include_deleted)

    if not worker:
        raise Exception("Worker not found")
    
    return worker


async def worker_exists(db: Session, user_id: UUID):
    stmt = select(exists().where(Worker.user_id == user_id, Worker.deleted_at.is_not(None)))
    result = await db.execute(stmt)
    return result.scalar()
