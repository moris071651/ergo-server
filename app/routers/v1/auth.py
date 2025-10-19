from datetime import datetime, timezone
import json
from uuid import UUID
from fastapi import APIRouter, Body, Depends, Request, Response, status
from fastapi.responses import JSONResponse

from app.db.session import Session, get_db
from app.config.settings import AUTH_COOKIE_KEY, AUTH_COOKIE_HTTPONLY, AUTH_COOKIE_MAX_AGE, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_SECURE
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException
from app.schemas.auth import AuthSessionInfo, UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.token import create_access_token, revoke_token
from app.services import auth as service


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
async def signup(
    req: Request,
    res: Response,
    new_user: UserSignupRequest = Body(),
    db: Session = Depends(get_db)
) -> UserAuthResponse:
    if req.state.user is not None:
        raise UserAlreadyLoggedInException()

    user = await service.signup(new_user, db)
    access_token = create_access_token({"id": str(user.id)})

    res.status_code = status.HTTP_201_CREATED
    res.set_cookie(
        key = AUTH_COOKIE_KEY,
        value = access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = AUTH_COOKIE_MAX_AGE
    )

    return user


@router.post('/login')
async def login(
    req: Request,
    res: Response,
    credentials: UserLoginRequest = Body(),
    db: Session = Depends(get_db)
) -> UserAuthResponse:
    if req.state.user is not None:
        raise UserAlreadyLoggedInException()

    user = await service.login(credentials, db)
    access_token = create_access_token({"id": str(user.id)})

    res.status_code = status.HTTP_200_OK
    res.set_cookie(
        key = AUTH_COOKIE_KEY,
        value = access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = AUTH_COOKIE_MAX_AGE
    )

    return user


@router.get('/login')
async def get_session_info(req: Request) -> AuthSessionInfo:
    if req.state.user is None:
        raise UserNotLoggedInException()
    
    jwt = req.state.jwt

    return AuthSessionInfo(
        user_id = UUID(jwt.get("id")),
        issued_at = datetime.fromtimestamp(jwt.get("iat"), timezone.utc),
        expires_at = datetime.fromtimestamp(jwt.get("exp"), timezone.utc),
        jti = UUID(jwt.get("jti"))
    )


@router.delete('/logout')
async def logout(
    req: Request,
    res: Response
):
    if req.state.user is None:
        raise UserNotLoggedInException()
    
    await revoke_token(
        jti = req.state.jwt['jti'],
        exp_timestamp = req.state.jwt['exp']
    )
    
    res.status_code = status.HTTP_204_NO_CONTENT
    res.delete_cookie(
        key = AUTH_COOKIE_KEY,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE
    )
