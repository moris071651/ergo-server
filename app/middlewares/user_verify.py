from typing import Annotated
from uuid import UUID
from fastapi import Depends, Request
from app.config.settings import AUTH_ACCESS_COOKIE_KEY

from app.db.session import get_db
from app.exceptions.auth import UserNotLoggedInException
from app.models.users import User
from app.utils.token import get_access_token_data
from app.utils.user import fetch_user, user_exists


async def get_current_user_id(req: Request):
    access_token = req.cookies.get(AUTH_ACCESS_COOKIE_KEY)

    user_id = None
    if access_token:
        try:
            data = await get_access_token_data(access_token)
            print(data)
            user_id = data.get("id")

        except Exception as e:
            pass

    ret = None
    if user_id:
        async for db in get_db():
            if await user_exists(db, user_id):
                ret = UUID(user_id)
            break

    return ret


async def get_current_user_id_panic(req: Request):
    user_id = await get_current_user_id(req)

    if not user_id:
        raise UserNotLoggedInException()

    return user_id

CurrentUserIdPanicDep = Annotated[
    UUID,
    Depends(get_current_user_id_panic)
]


async def get_current_user(req: Request):
    access_token = req.cookies.get(AUTH_ACCESS_COOKIE_KEY)

    user_id = None
    if access_token:
        try:
            data = await get_access_token_data(access_token)
            user_id = data.get("id")
            
        except Exception:
            pass

    ret = None
    if user_id:
        async for db in get_db():
            ret = await fetch_user(db, user_id)
            break

    return ret


async def get_current_user_panic(req: Request):
    user = await get_current_user(req)

    if not user:
        raise UserNotLoggedInException()
    
    return user


CurrentUserIdDep = Annotated[
    UUID | None,
    Depends(get_current_user_id)
]


CurrentUserIdPanicDep = Annotated[
    UUID,
    Depends(get_current_user_id_panic)
]


CurrentUserDep = Annotated[
    User | None,
    Depends(get_current_user)
]


CurrentUserPanicDep = Annotated[
    User,
    Depends(get_current_user_panic)
]
