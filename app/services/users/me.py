import io
from pathlib import Path
from PIL import Image, ImageOps
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
import mimetypes

from app.config.settings import BUCKET_USER_PICTURE
from app.exceptions.file import FileCreationFailedException, FileDeletionFailedException, FileFetchingFailedException, NotImageFormatException
from app.exceptions.users import EmailUsedExistsException

from app.db.session import Session
from app.schemas.users import CurrentUserResponse, UpdateUserRequest, UserPictureResponse
from app.utils.storage.base import StorageAdapter
from app.utils.user import email_available, fetch_user


async def get_current_user(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
):
    user = await fetch_user(db, user_id)
    url = storage.create_presigned_url(BUCKET_USER_PICTURE, user.profile_image_key, expires_seconds=3600)
    return CurrentUserResponse.model_validate({**user.__dict__, "profile_image_url": url})
    

async def update_current_user(
    user_id: UUID,
    update: UpdateUserRequest,
    db: Session,
    storage: StorageAdapter
) -> CurrentUserResponse:
    user = await fetch_user(db, user_id)
    
    for key, value in update.model_dump(
        exclude_unset = True,
        exclude_none = True
    ).items():
        if key == 'email' and not await email_available(db, value):
            raise EmailUsedExistsException()

        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    url = storage.create_presigned_url(BUCKET_USER_PICTURE, user.profile_image_key, expires_seconds=3600)
    return CurrentUserResponse.model_validate({**user.__dict__, "profile_image_url": url})


async def deactivate_current_user(
    user_id: UUID,
    db: Session
):
    user = await fetch_user(db, user_id)
    user.deleted_at = datetime.utcnow()
    await db.commit()


async def get_current_user_picture(
    user_id: UUID,
    db: Session,
    storage: StorageAdapter
) -> UserPictureResponse:
    user = await fetch_user(db, user_id)

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
    filename = file_name or "upload.bin"
    mime_type, _ = mimetypes.guess_type(filename, strict=False)
    mime_type = mime_type or "application/octet-stream"

    if not mime_type.startswith("image/"):
        ext = Path(filename).suffix.lower() or ".bin"
        raise NotImageFormatException(user_id, ext)

    key = f"pfp/{user_id}/{uuid4()}.jpeg"

    try:
        img = Image.open(io.BytesIO(file_bytes))
        img = ImageOps.exif_transpose(img)

        if img.mode != "RGB":
            img = img.convert("RGB")

        output = io.BytesIO()
        img_format = "JPEG"

        img.save(output, format=img_format) 
        clean_bytes = output.getvalue()

        storage.put_object(BUCKET_USER_PICTURE, key, clean_bytes, content_type="image/jpeg")
        file_url = storage.create_presigned_url(BUCKET_USER_PICTURE, key, expires_seconds=86400)

        user = await fetch_user(db, user_id)
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
):
    user = await fetch_user(db, user_id)

    if not user.profile_image_key:
        return
        
    key = user.profile_image_key

    try:
        storage.delete_object(BUCKET_USER_PICTURE, key)
        user.profile_image_key = None

        await db.commit()
        await db.refresh(user)

    except Exception as e:
        raise FileDeletionFailedException(str(e))
