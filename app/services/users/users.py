from uuid import UUID

from sqlalchemy import select
from app.config.settings import BUCKET_USER_PICTURE

from app.db.session import Session
from app.models.users import User
from app.schemas.users import UserResponse
from app.utils.storage.base import StorageAdapter
from app.utils.user import user_exists


async def get_users():
    raise NotImplementedError


async def get_user(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
):
    if not user_exists(db, user_id):
        raise Exception
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    profile_image_url = storage.create_presigned_url(BUCKET_USER_PICTURE, user.profile_image_key)
    
    return UserResponse(
        id = user.id,
        email = user.email,
        profile_image_url = profile_image_url,
        first_name = user.first_name,
        last_name = user.last_name,
        created_at = user.created_at
    )


async def get_user_picture(user_id: UUID):

    raise NotImplementedError
