

from uuid import UUID
from sqlalchemy import select
from app.db.session import Session
from app.exceptions.auth import InvalidCredentialsException, UserAlreadyExistsException
from app.models.users import User
from app.schemas.auth import UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.password import hash_password, verify_password


async def signup(new_user: UserSignupRequest, db: Session) -> UserAuthResponse:
    existing_user = (await db.execute(
        select(User).filter(
            (User.username == new_user.username) | (User.email == new_user.email)
        )
    )).scalars().first()

    if existing_user is not None:
        raise UserAlreadyExistsException()
    
    hashed_password = hash_password(new_user.password)

    user = User(
        email = new_user.email,
        username = new_user.username,
        hashed_password = hashed_password
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserAuthResponse(
        id = user.id,
        username = user.username,
        email = user.email,
    ) 


async def login(credentials: UserLoginRequest, db: Session) -> UserAuthResponse:
    user = (await db.execute(
        select(User).filter(
            (User.email == credentials.email)
        )
    )).scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise InvalidCredentialsException()
    
    return UserAuthResponse(
        id = user.id,
        username = user.username,
        email = user.email,
    )


def get_session_info():
    pass


def logout():
    pass