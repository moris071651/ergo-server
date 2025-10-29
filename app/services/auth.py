from sqlalchemy import select
from app.db.session import Session
from app.exceptions.auth import InvalidCredentialsException, UserAlreadyExistsException
from app.models.users import User
from app.schemas.auth import UserAuthResponse, UserLoginRequest, UserSignupRequest
from app.utils.password import hash_password, verify_password
from app.utils.user import email_available


async def signup(new_user: UserSignupRequest, db: Session) -> UserAuthResponse:
    if not await email_available(db, new_user.email):
        raise UserAlreadyExistsException()
    
    hashed_password = hash_password(new_user.password)

    user = User(
        email = new_user.email,
        first_name = new_user.first_name,
        last_name = new_user.last_name,
        hashed_password = hashed_password
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserAuthResponse(
        id = user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email = user.email
    ) 


async def login(credentials: UserLoginRequest, db: Session) -> UserAuthResponse:
    result = await db.execute(select(User).filter(User.email == credentials.email))
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise InvalidCredentialsException()
    
    return UserAuthResponse(
        id = user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email = user.email,
    )


def get_session_info():
    pass


def logout():
    pass