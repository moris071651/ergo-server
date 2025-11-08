from fastapi import APIRouter, Depends, Request, status

from app.db.session import Session, get_db
from app.exceptions.auth import UserNotLoggedInException


router = APIRouter(prefix='/me')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def register_worker(
    req: Request,
    db: Session = Depends(get_db)
) -> CurrentWorkerResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    pass


@router.get('/')
async def get_my_worker_profile(
    req: Request,
    db: Session = Depends(get_db)
) -> CurrentWorkerResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    pass


@router.patch('/')
async def update_worker_profile(
    req: Request,
    db: Session = Depends(get_db)
) -> CurrentWorkerResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    pass


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker_profile(
    req: Request,
    db: Session = Depends(get_db)
):
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    pass
