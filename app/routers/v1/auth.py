from fastapi import APIRouter, Body, Depends, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app.db.session import AsyncSessionLocal, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.auth import UserAlreadyExistsException, UserAlreadyLoggedInException, UserNotLoggedInException
from app.models.users import User
from app.schemas.users import UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.password import hash_password
from app.utils.token import create_access_token


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/signup')
async def signup(req: Request, new_user: UserSignupRequest = Body(), db: AsyncSession = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserAlreadyLoggedInException()
    
    existing_user = (await db.execute(
        select(User).filter(
            (User.username == new_user.username) | (User.email == new_user.email)
        )
    )).scalars().first()

    if existing_user is not None:
        raise UserAlreadyExistsException()
    
    hashed_password = hash_password(new_user.password)

    user = User(
        username = new_user.username,
        email = new_user.email,
        hashed_password = hashed_password
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token({"user_id": str(user.id)})

    res = JSONResponse(
        content = UserAuthResponse(
            id=user.id,
            username=user.username,
            email=user.email,
        ).model_dump()
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
def login(req: Request, new_user: UserLoginRequest = Body(), db: AsyncSession = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserAlreadyLoggedInException()


@router.get('/login')
def get_session_info(req: Request, db: AsyncSession = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserNotLoggedInException()


@router.delete('/logout')
def logout(req: Request, db: AsyncSession = Depends(get_db)):
    if req.state.user_id is not None:
        raise UserNotLoggedInException()
