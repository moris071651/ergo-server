from fastapi import APIRouter, Depends, Request, status

from app.db.session import Session, get_db
from app.exceptions.auth import UserNotLoggedInException


router = APIRouter(prefix='/me')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def activate_worker(
    req: Request,
    worker_data: WorkerCreate,
    db: Session = Depends(get_db)
) -> CurrentWorkerResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.activate_worker(db, user_id, worker_data)


@router.get('/')
async def get_my_worker_profile(
    req: Request,
    db: Session = Depends(get_db)
) -> CurrentWorkerResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_my_worker_profile(db, user_id)


@router.patch('/')
async def update_worker_profile(
    req: Request,
    worker_data: WorkerUpdate,
    db: Session = Depends(get_db)
) -> CurrentWorkerResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.update_worker_profile(db, user_id, worker_data)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_worker_profile(
    req: Request,
    db: Session = Depends(get_db)
):
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    await service.deactivate_worker_profile(db, user_id)
