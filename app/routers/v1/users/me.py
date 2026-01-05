from fastapi import APIRouter, Request, Response, status
from app.config.settings import AUTH_COOKIE_KEY
from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep

from app.schemas.users import CurrentUserResponse, UpdateUserRequest, UserPictureResponse
from app.services.users import me as service
from app.utils.storage import FileArg, StorageAdapterDep
from app.utils.token import revoke_token


router = APIRouter(prefix='/me', tags=['Current user'])


@router.get('', response_model=CurrentUserResponse)
async def get_current_user(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep
):
    return await service.get_current_user(user_id, db, storage)


@router.patch('')
async def update_current_user(
    update: UpdateUserRequest,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> CurrentUserResponse:
    return await service.update_current_user(user_id, update, db)


@router.delete('')
async def deactivate_current_user(
    req: Request,
    res: Response,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    await service.deactivate_current_user(user_id, db)

    await revoke_token(
        jti = req.state.jwt['jti'],
        exp_timestamp = req.state.jwt['exp']
    )

    res.status_code = status.HTTP_204_NO_CONTENT
    res.delete_cookie(AUTH_COOKIE_KEY)


@router.get('/picture')
async def get_current_user_picture(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep
) -> UserPictureResponse:
    return await service.get_current_user_picture(user_id, db, storage)


@router.put('/picture')
async def update_current_user_picture(
    file: FileArg,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep
) -> UserPictureResponse:
    return await service.update_current_user_picture(
        file_bytes = await file.read(),
        file_name = file.filename,
        storage = storage,
        user_id = user_id,
        db = db
    )


@router.delete('/picture')
async def delete_current_user_picture(
    res: Response,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep
):
    await service.delete_current_user_picture(user_id, db, storage)
    res.status_code = status.HTTP_204_NO_CONTENT
