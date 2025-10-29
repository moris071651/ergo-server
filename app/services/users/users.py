from uuid import UUID

from app.db.session import Session
from app.config.settings import BUCKET_USER_PICTURE
from app.schemas.users import UserPictureResponse, UserResponse
from app.utils.storage.base import StorageAdapter
from app.utils.user import fetch_user, user_exists


async def get_users():
    raise NotImplementedError


async def get_user(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
) -> UserResponse:
    if not user_exists(db, user_id):
        raise Exception
    
    user = fetch_user(db, user_id)
    profile_image_url = storage.create_presigned_url(BUCKET_USER_PICTURE, user.profile_image_key)
    
    return UserResponse(
        id = user.id,
        email = user.email,
        profile_image_url = profile_image_url,
        first_name = user.first_name,
        last_name = user.last_name,
        created_at = user.created_at
    )


async def get_user_picture(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
) -> UserPictureResponse:
    if not user_exists(db, user_id):
        raise Exception
    
    user = fetch_user(db, user_id)
    profile_image_url = storage.create_presigned_url(BUCKET_USER_PICTURE, user.profile_image_key)

    return UserPictureResponse(
        profile_image_url=profile_image_url
    )
