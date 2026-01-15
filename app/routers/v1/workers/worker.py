from typing import List
from uuid import UUID
from fastapi import APIRouter

from app.db.session import DBSessionDep
from app.schemas.workers import WorkerResponse
from app.services.workers import worker as service


router = APIRouter(tags=["Worker"])


@router.get('/{user_id}')
async def get_worker_profile(
    user_id: UUID,
    db: DBSessionDep
) -> WorkerResponse:
    return await service.get_worker_profile(db, user_id)


@router.get('/')
async def get_all_worker_profiles(
    db: DBSessionDep,
) -> List[WorkerResponse]:
    return await service.get_all_worker_profiles(db)
