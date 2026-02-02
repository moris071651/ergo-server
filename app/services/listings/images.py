import io
import mimetypes
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import func, select
from PIL import Image, ImageOps
from app.config.settings import BUCKET_LISTING_IMAGES

from app.db.session import Session
from app.exceptions.file import FileCreationFailedException, NotImageFormatException
from app.models.listing_images import ListingImage
from app.schemas.listings import ListingImageResponse
from app.utils.storage.base import StorageAdapter


async def _get_max_order(db, listing_id):
    stmt = (
        select(func.max(ListingImage.sort_order))
        .where(ListingImage.listing_id == listing_id)
    )
    result = await db.execute(stmt)
    current_max_sort = result.scalars().first()
    return current_max_sort if current_max_sort is not None else -1


async def _get_primary_image(db, listing_id):
    stmt = (
        select(ListingImage)
        .where(ListingImage.listing_id == listing_id)
        .where(ListingImage.is_primary == True)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def _get_images(db, listing_id):
    stmt = (
        select(ListingImage)
        .where(ListingImage.listing_id == listing_id)
        .order_by(ListingImage.sort_order)
    )
    result = await db.execute(stmt)
    return result.scalars().all() or []


async def upload_listing_images(
    db: Session,
    storage: StorageAdapter,
    user_id: UUID,
    listing_id: UUID,
    images: list[UploadFile]
) -> ListingImageResponse:
    uploads = []

    for image in images:
        filename = image.filename or "upload.bin"
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or image.content_type or "application/octet-stream"

        if not mime_type.startswith("image/"):
            ext = Path(filename).suffix.lower() or ".bin"
            raise NotImageFormatException(user_id, ext)

        key = f"listing/{listing_id}/{uuid4()}.jpeg"

        uploads.append({
            "key": key,
            "file": image.file,
            "mime_type": mime_type
        })

    uploaded_keys = []
    created_images = []
    max_order = await _get_max_order(db, listing_id)

    try:
        for upload in uploads:
            img = Image.open(io.BytesIO(upload["file"]))
            img = ImageOps.exif_transpose(img)

            if img.mode != "RGB":
                img = img.convert("RGB")

            output = io.BytesIO()
            img_format = "JPEG"

            img.save(output, format=img_format) 
            clean_bytes = output.getvalue()

            storage.put_object(
                BUCKET_LISTING_IMAGES,
                upload["key"],
                clean_bytes,
                content_type="image/jpeg",
            )

            uploaded_keys.append(upload["key"])

            image_row = ListingImage(
                listing_id=listing_id,
                object_key=upload["key"],
                is_primary=(max_order == -1),
                sort_order=max_order + 1,
            )

            db.add(image_row)
            created_images.append(image_row)
            max_order += 1

        db.commit()

    except Exception as e:
        db.rollback()

        for key in uploaded_keys:
            try:
                storage.delete_object(BUCKET_LISTING_IMAGES, key)

            except Exception:
                pass

        raise FileCreationFailedException(str(e))

    ret = []
    for image in created_images:
        db.refresh(image)

        url = storage.create_presigned_url(
            BUCKET_LISTING_IMAGES,
            image.object_key,
            expires_seconds=86400,
        )

        ret.append(
            ListingImageResponse(
                id=image.id,
                url=url,
                is_primary=image.is_primary,
                sort_order=image.sort_order,
            )
        )

    return ret


async def get_listing_images(
    db: Session,
    storage: StorageAdapter,
    user_id: UUID,
    listing_id: UUID,
) -> list[ListingImageResponse]:
    images = await _get_images(db, listing_id)

    responses = []
    for image in images:
        url = storage.create_presigned_url(
            BUCKET_LISTING_IMAGES,
            image.object_key,
            expires_seconds=86400,
        )
        responses.append(
            ListingImageResponse.model_validate(image).model_copy(update={"url": url})
        )

    return responses


async def make_listing_images_primary(
    db: Session,
    storage: StorageAdapter,
    user_id: UUID,
    listing_id: UUID,
    image_id: UUID
) -> ListingImageResponse:
    images = await _get_images(db, listing_id)

    if not images:
        raise HTTPException(status_code=404, detail="No images found for this listing")

    target_image = next((img for img in images if img.id == image_id), None)
    if not target_image:
        raise HTTPException(status_code=404, detail="Image not found")

    for img in images:
        img.is_primary = (img.id == image_id)

    db.commit()
    db.refresh(target_image)

    url = storage.create_presigned_url(
        BUCKET_LISTING_IMAGES,
        target_image.object_key,
        expires_seconds=86400,
    )

    return ListingImageResponse.model_validate(target_image).model_copy(update={"url": url})


async def get_listing_images_primary(
    db: Session,
    storage: StorageAdapter,
    user_id: UUID,
    listing_id: UUID
) -> ListingImageResponse:
    primary_image = await _get_primary_image(db, listing_id)

    if not primary_image:
        raise HTTPException(status_code=404, detail="No primary image found")

    url = storage.create_presigned_url(BUCKET_LISTING_IMAGES, primary_image.object_key, expires_seconds=86400)
    return ListingImageResponse.model_validate(primary_image).model_copy(update={"url": url})


async def delete_listing_image(
    db: Session,
    storage: StorageAdapter,
    user_id: UUID,
    listing_id: UUID,
    image_id: UUID
):
    images = await _get_images(db, listing_id)

    target = next((img for img in images if img.id == image_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Image not found")

    storage.delete_object(BUCKET_LISTING_IMAGES, target.object_key)
    db.delete(target)
    db.commit()

    remaining_images = await _get_images(db, listing_id)
    if remaining_images:
        for index, img in enumerate(sorted(remaining_images, key=lambda x: x.sort_order)):
            img.sort_order = index

        if not any(img.is_primary for img in remaining_images):
            remaining_images[0].is_primary = True

        db.commit()
        for img in remaining_images:
            db.refresh(img)
