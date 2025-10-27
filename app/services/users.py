from datetime import datetime
import mimetypes
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from app.config.settings import BUCKET_USER_PICTURE
from app.exceptions.file import FileCreationFailedException, FileDeletionFailedException, FileFetchingFailedException, NotImageFormatException
from app.exceptions.users import EmailUsedExistsException

from app.models.users import User
from app.db.session import Session
from app.schemas.users import CurrentUserResponse, UpdateUserRequest, UserPictureResponse
from app.utils.storage.base import StorageAdapter
from app.utils.user import email_available


async def get_current_user(
    user_id: UUID,
    db: Session
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    return CurrentUserResponse(
        id = user.id,
        email = user.email,
        profile_image_url = user.profile_image_url,
        first_name = user.first_name,
        last_name = user.last_name,
        created_at = user.created_at,
        updated_at = user.updated_at
    )


async def update_current_user(
    user_id: UUID,
    update: UpdateUserRequest,
    db: Session
) -> CurrentUserResponse:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    for key, value in update.model_dump(
        exclude_unset = True,
        exclude_none = True
    ).items():
        if key == 'email' and not await email_available(db, value):
            raise EmailUsedExistsException()

        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return CurrentUserResponse(
        id = user.id,
        email = user.email,
        profile_image_url = user.profile_image_url,
        first_name = user.first_name,
        last_name = user.last_name,
        created_at = user.created_at,
        updated_at = user.updated_at
    )


async def deactivate_current_user(
    user_id: UUID,
    db: Session
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    user.deleted_at = datetime.utcnow()
    await db.commit()


async def get_current_user_picture(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
) -> UserPictureResponse:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user.profile_image_key:
        return UserPictureResponse(
            profile_image_url=None
        )

    try:
        url = storage.create_presigned_url(BUCKET_USER_PICTURE, user.profile_image_key, expires_seconds=3600)
        return UserPictureResponse(
            profile_image_url=url
        )

    except Exception as e:
        raise FileFetchingFailedException(str(e))
    

async def update_current_user_picture(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter,
    file_name: Optional[str],
    file_bytes: bytes
) -> UserPictureResponse:
    filename = file_name or "upload"
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or "application/octet-stream"
    ext = mimetypes.guess_extension(mime_type) or ".bin"

    if not mime_type.startswith("image/"):
        raise NotImageFormatException(user_id, ext)

    key = f"{user_id}/{uuid4()}{ext}"

    try:
        storage.put_object("user-pictures", key, file_bytes, content_type=mime_type)
        file_url = storage.create_presigned_url(BUCKET_USER_PICTURE, key, expires_seconds=86400)

        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        user.profile_image_key = key
        await db.commit()

        return UserPictureResponse(
            profile_image_url=file_url
        )

    except Exception as e:
        raise FileCreationFailedException(str(e))


async def delete_current_user_picture(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
) -> UserPictureResponse:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user.profile_image_key:
        return # do nothing 
        
    key = user.profile_image_key

    try:
        storage.delete_object(BUCKET_USER_PICTURE, key)
        user.profile_image_key = None

        await db.commit()
        await db.refresh(user)

    except Exception as e:
        raise FileDeletionFailedException(str(e))
