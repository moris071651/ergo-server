from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.responses import JSONResponse

from app.db.session import Session, get_db
from app.config.settings import AUTH_COOKIE_KEY, AUTH_COOKIE_HTTPONLY, AUTH_COOKIE_MAX_AGE, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_SECURE
from app.exceptions.auth import UserAlreadyLoggedInException, UserNotLoggedInException
from app.schemas.users import UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.token import create_access_token
from app.services import auth as service


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
async def signup(
    req: Request,
    new_user: UserSignupRequest = Body(),
    db: Session = Depends(get_db)
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
        key = AUTH_COOKIE_KEY,
        value = access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = AUTH_COOKIE_MAX_AGE
    )

    return res


@router.post('/login')
async def login(
    req: Request,
    credentials: UserLoginRequest = Body(),
    db: Session = Depends(get_db)
) -> UserAuthResponse:
    if req.state.user_id is not None:
        raise UserAlreadyLoggedInException()

    user = service.login(credentials, db)
    access_token = create_access_token({"user_id": str(user.id)})

    res = JSONResponse(
        content=user.model_dump(),
        status_code = status.HTTP_200_OK
    )

    res.set_cookie(
        key = AUTH_COOKIE_KEY,
        value = access_token,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE,
        max_age = AUTH_COOKIE_MAX_AGE
    )

    return res


@router.get('/login')
def get_session_info(req: Request, db: Session = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserNotLoggedInException()


@router.delete('/logout')
async def logout(req: Request, db: Session = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserNotLoggedInException()
    
    response = JSONResponse(status_code = status.HTTP_204_NO_CONTENT)

    response.delete_cookie(
        key = AUTH_COOKIE_KEY,
        httponly = AUTH_COOKIE_HTTPONLY,
        secure = AUTH_COOKIE_SECURE,
        samesite = AUTH_COOKIE_SAMESITE
    )
