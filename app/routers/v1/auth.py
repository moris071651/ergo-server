from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException
from app.models.users import User
from app.schemas.users import UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.password import verify_password
from app.utils.token import create_access_token
from app.services import auth as service


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
async def signup(
    req: Request,
    new_user: UserSignupRequest = Body(),
    db: AsyncSession = Depends(get_db)
) -> UserAuthResponse:
    if req.state.user_id is not None:
        raise UserAlreadyLoggedInException()

    user = await service.signup(new_user, db)
    access_token = create_access_token({"user_id": str(user.id)})

    res = JSONResponse(
        content = user.model_dump(),
        status_code = status.HTTP_201_CREATED
    )

    res.set_cookie(
        key = 'ErgoAuthToken',
        value = access_token,
        # httponly = True,
        # secure = True,
        # samesite = 'lax',
        # max_age = 3600
    )

    return res



@router.post('/login')
async def login(
    req: Request,
    credentials: UserLoginRequest = Body(),
    db: AsyncSession = Depends(get_db)
) -> UserAuthResponse:
    if req.state.user_id is not None:
        raise UserAlreadyLoggedInException()

    user = service.login(credentials, db)
    access_token = create_access_token({"user_id": str(user.id)})

    response = JSONResponse(
        content=user.model_dump(),
        status_code = status.HTTP_200_OK
    )

    response.set_cookie(
        key = "ErgoAuthToken",
        value = access_token,
        # httponly=True,
        # secure=True,
        # samesite="lax",
        # max_age=3600
    )

    return response


@router.get('/login')
def get_session_info(req: Request, db: AsyncSession = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserNotLoggedInException()


@router.delete('/logout')
def logout(req: Request, db: AsyncSession = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserNotLoggedInException()
