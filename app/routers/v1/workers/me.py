from typing import Optional
from fastapi import APIRouter, status

from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.services.workers import me as service
from app.schemas.workers import CurrentWorkerResponse, WorkerCreate, WorkerUpdate


router = APIRouter(prefix='/me', tags=["Current worker"])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_worker(
    worker_data: Optional[WorkerCreate],
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> CurrentWorkerResponse:
    return await service.create_worker(db, user_id, worker_data)


@router.get('/')
async def get_my_worker_profile(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> CurrentWorkerResponse:
    return await service.get_my_worker_profile(db, user_id)


@router.patch('/')
async def update_worker_profile(
    worker_data: WorkerUpdate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> CurrentWorkerResponse:
    return await service.update_worker_profile(db, user_id, worker_data)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_worker_profile(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    await service.deactivate_worker_profile(db, user_id)
