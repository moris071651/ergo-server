from fastapi import APIRouter, Depends, File, Request, Response, UploadFile, status
from app.config.settings import AUTH_COOKIE_KEY
from app.db.session import Session, get_db

from app.exceptions.auth import UserNotLoggedInException
from app.schemas.users import CurrentUserResponse, UpdateUserRequest, UserPictureResponse
from app.services import users as service
from app.utils.storage import get_storage_adapter
from app.utils.storage.base import StorageAdapter
from app.utils.token import revoke_token


router = APIRouter(prefix='/users', tags=['Users'])


@router.get("/me")
async def get_current_user(
    req: Request,
    db: Session = Depends(get_db)
) -> CurrentUserResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_current_user(user_id, db)


@router.patch('/me')
async def update_current_user(
    req: Request,
    update: UpdateUserRequest,
    db: Session = Depends(get_db)
) -> CurrentUserResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.update_current_user(user_id, update, db)


@router.delete('/me')
async def deactivate_current_user(
    req: Request,
    res: Response,
    db: Session = Depends(get_db)
):
    if req.state.user is None:
        raise UserNotLoggedInException()
    
    user_id = req.state.user_id
    await service.deactivate_current_user(user_id, db)

    await revoke_token(
        jti = req.state.jwt['jti'],
        exp_timestamp = req.state.jwt['exp']
    )

    res.status_code = status.HTTP_204_NO_CONTENT
    res.delete_cookie(AUTH_COOKIE_KEY)


@router.get('/me/picture')
async def get_current_user_picture(
    req: Request,
    db: Session = Depends(get_db)
) -> UserPictureResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_current_user_picture(user_id, db)


@router.put('/me/picture')
async def update_current_user_picture(
    req: Request,
    file: UploadFile = File(...),
    storage: StorageAdapter = Depends(get_storage_adapter),
    db: Session = Depends(get_db)
) -> UserPictureResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.update_current_user_picture(
        file_bytes = await file.read(),
        file_name = file.filename,
        storage = storage,
        user_id = user_id,
        db = db
    )


@router.delete('/me/picture')
async def delete_current_user_picture(
    req: Request,
    res: Response,
    db: Session = Depends(get_db)
):
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    await service.delete_current_user_picture(user_id, db)
    res.status_code = status.HTTP_204_NO_CONTENT
