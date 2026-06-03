from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Request, Response, status

from app.db.session import DBSessionDep
from app.config.settings import ACCESS_TOKEN_EXPIRE, AUTH_ACCESS_COOKIE_KEY, AUTH_COOKIE_HTTPONLY, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_SECURE, AUTH_REFRESH_COOKIE_KEY, REFRESH_TOKEN_EXPIRE
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException
from app.middlewares.user_verify import CurrentUserIdDep, CurrentUserIdPanicDep
from app.schemas.auth import AuthSessionInfo, UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.token import create_access_token, create_session, get_access_token_payload, invalidate_session, mark_access_token_active, refresh_session, verify_refresh_token
from app.services import auth as service


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(
    req: Request,
    res: Response,
    new_user: UserSignupRequest,
    db: DBSessionDep,
    user_id: CurrentUserIdDep
) -> UserAuthResponse:
    if user_id is not None:
        raise UserAlreadyLoggedInException()
    
    refresh_token = req.cookies.get(AUTH_REFRESH_COOKIE_KEY)
    if await verify_refresh_token(refresh_token):
        raise UserAlreadyLoggedInException()

    user = await service.signup(new_user, db)
    refresh_token, _sid = await create_session(str(user.id))

    access_token = create_access_token({"id": str(user.id)})
    await mark_access_token_active(access_token)

    res.set_cookie(
        key = AUTH_ACCESS_COOKIE_KEY,
        value = access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = ACCESS_TOKEN_EXPIRE
    )

    res.set_cookie(
        key = AUTH_REFRESH_COOKIE_KEY,
        value = refresh_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = REFRESH_TOKEN_EXPIRE
    )

    return user


@router.post('/login')
async def login(
    req: Request,
    res: Response,
    credentials: UserLoginRequest,
    db: DBSessionDep,
    user_id: CurrentUserIdDep
) -> UserAuthResponse:
    if user_id is not None:
        raise UserAlreadyLoggedInException()
    
    refresh_token = req.cookies.get(AUTH_REFRESH_COOKIE_KEY)
    if await verify_refresh_token(refresh_token):
        raise UserAlreadyLoggedInException()
    
    user = await service.login(credentials, db)
    refresh_token, _sid = await create_session(str(user.id))

    access_token = create_access_token({"id": str(user.id)})
    await mark_access_token_active(access_token)

    res.set_cookie(
        key = AUTH_ACCESS_COOKIE_KEY,
        value = access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = ACCESS_TOKEN_EXPIRE
    )

    res.set_cookie(
        key = AUTH_REFRESH_COOKIE_KEY,
        value = refresh_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = REFRESH_TOKEN_EXPIRE
    )

    return user


@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh(req: Request, res: Response):
    refresh_token = req.cookies.get(AUTH_REFRESH_COOKIE_KEY)
    access_token = req.cookies.get(AUTH_ACCESS_COOKIE_KEY)

    if not refresh_token:
        raise UserNotLoggedInException()
    
    new_access_token, new_refresh_token = await refresh_session(
        refresh_token=refresh_token,
        access_token=access_token,
    )

    res.set_cookie(
        key=AUTH_ACCESS_COOKIE_KEY,
        value=new_access_token,
        httponly=AUTH_COOKIE_HTTPONLY,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        max_age=ACCESS_TOKEN_EXPIRE,
    )

    res.set_cookie(
        key=AUTH_REFRESH_COOKIE_KEY,
        value=new_refresh_token,
        httponly=AUTH_COOKIE_HTTPONLY,
        secure=AUTH_COOKIE_SECURE,
        samesite=AUTH_COOKIE_SAMESITE,
        max_age=REFRESH_TOKEN_EXPIRE,
    )


@router.get('/login')
async def get_session_info(
    req: Request,
    user_id: CurrentUserIdPanicDep
) -> AuthSessionInfo:
    access_token = req.cookies.get(AUTH_ACCESS_COOKIE_KEY)
    payload = await get_access_token_payload(access_token)

    return AuthSessionInfo(
        user_id = user_id,
        issued_at = datetime.fromtimestamp(payload.get("iat"), timezone.utc),
        expires_at = datetime.fromtimestamp(payload.get("exp"), timezone.utc),
        jti = UUID(payload.get("jti"))
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: Request, res: Response):
    refresh_token = req.cookies.get(AUTH_REFRESH_COOKIE_KEY)
    access_token = req.cookies.get(AUTH_ACCESS_COOKIE_KEY)

    if not refresh_token:
        res.delete_cookie(AUTH_ACCESS_COOKIE_KEY)
        res.delete_cookie(AUTH_REFRESH_COOKIE_KEY)
        return

    await invalidate_session(
        refresh_token=refresh_token,
        access_token=access_token,
    )

    res.delete_cookie(AUTH_ACCESS_COOKIE_KEY)
    res.delete_cookie(AUTH_REFRESH_COOKIE_KEY)
