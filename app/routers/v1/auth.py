from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.db.session import DBSessionDep
from app.config.settings import ACCESS_TOKEN_EXPIRE, AUTH_ACCESS_COOKIE_KEY, AUTH_COOKIE_HTTPONLY, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_SECURE, AUTH_REFRESH_COOKIE_KEY, REFRESH_TOKEN_EXPIRE
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException
from app.middlewares.user_verify import CurrentUserIdDep
from app.schemas.auth import AuthSessionInfo, UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.token import create_access_token, create_refresh_token, decode_token, invalidate_session, is_token_revoked
from app.services import auth as service


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(
    res: Response,
    new_user: UserSignupRequest,
    db: DBSessionDep,
    user_id: CurrentUserIdDep
) -> UserAuthResponse:
    if user_id is not None:
        raise UserAlreadyLoggedInException()

    user = await service.signup(new_user, db)
    access_token = create_access_token({"id": str(user.id)})
    refresh_token = create_refresh_token({"id": str(user.id)})

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
    res: Response,
    credentials: UserLoginRequest,
    db: DBSessionDep,
    user_id: CurrentUserIdDep
) -> UserAuthResponse:
    if user_id is not None:
        raise UserAlreadyLoggedInException()

    user = await service.login(credentials, db)
    access_token = create_access_token({"id": str(user.id)})
    refresh_token = create_refresh_token({"id": str(user.id)})

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


@router.post("/refresh")
async def refresh(req: Request, res: Response):
    refresh_token = req.cookies.get("refresh_token")
    if not refresh_token:
        raise UserNotLoggedInException()

    payload = decode_token(refresh_token, expected_type="refresh")

    if await is_token_revoked(payload["jti"]):
        raise HTTPException(status_code=401, detail="Token revoked")

    new_access_token = create_access_token({"id": payload["id"]})

    res.set_cookie(
        key = AUTH_ACCESS_COOKIE_KEY,
        value = new_access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = ACCESS_TOKEN_EXPIRE
    )

    return {"success": True}


@router.get('/login')
async def get_session_info(
    req: Request,
    user_id: CurrentUserIdDep
) -> AuthSessionInfo:
    if user_id is None:
        raise UserNotLoggedInException()
    
    jwt = req.state.jwt

    return AuthSessionInfo(
        user_id = UUID(jwt.get("id")),
        issued_at = datetime.fromtimestamp(jwt.get("iat"), timezone.utc),
        expires_at = datetime.fromtimestamp(jwt.get("exp"), timezone.utc),
        jti = UUID(jwt.get("jti"))
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(req: Request, res: Response):
    await invalidate_session(req, res)