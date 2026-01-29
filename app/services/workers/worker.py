from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from app.config.settings import BUCKET_USER_PICTURE
from app.db.session import Session
from app.models.address import Address
from app.models.booking import Booking
from app.models.users import User
from app.models.workers import Worker
from app.schemas.workers import PopularWorkerResponse, WorkerResponse
from app.utils.storage.base import StorageAdapter
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


async def get_popular_workers_profiles(
    db: Session,
    storage: StorageAdapter,
    filters: Optional[dict] = None
) -> List[PopularWorkerResponse]:
    stmt = (
        select(Worker)
        .where(Worker.deleted_at.is_(None))
        .options(
            joinedload(Worker.user),
            joinedload(Worker.address),
            joinedload(Worker.skills),
        )
    )

    stmt = (
        stmt.outerjoin(Worker.bookings)
        .group_by(Worker)
        .order_by(func.count(Booking.id).desc())
    )

    if filters:
        if "city" in filters and filters["city"]:
            city_filter = filters["city"].strip().lower()
            stmt = stmt.outerjoin(Worker.address).where(
                func.lower(Address.city).like(f"%{city_filter}%")
            )
        
        if "name" in filters and filters["name"]:
            name = filters["name"]
            stmt = stmt.outerjoin(Worker.user).where(
                (User.first_name + " " + User.last_name).ilike(f"%{name}%")
            )

        stmt = stmt.limit(filters.get("limit", 10))


    result = await db.execute(stmt)
    workers = result.scalars().unique().all()

    ret = []
    for worker in workers:
        url = None
        if worker.user.profile_image_key:
            url = storage.create_presigned_url(BUCKET_USER_PICTURE, worker.user.profile_image_key, expires_seconds=3600)

        tmp = PopularWorkerResponse.model_validate(worker)
        tmp.user.profile_image_url = url
        ret.append(tmp)

    return ret

