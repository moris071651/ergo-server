from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status
from app.db.session import DBSessionDep

from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.schemas.listings import ListingImageResponse
from app.services.listings import images as service
from app.utils.storage import StorageAdapterDep


ImagesDep = Annotated[List[UploadFile], File(...)]
router = APIRouter(tags=["Listing Images"])


@router.get("/listings/{listing_id}/images")
async def get_listing_images(
    listing_id: UUID,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep,
    db: DBSessionDep
) -> List[ListingImageResponse]:
    return await service.get_listing_images(db, storage, user_id, listing_id)


@router.post("/listings/{listing_id}/images")
async def upload_listing_images(
    listing_id: UUID,
    images: ImagesDep,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep,
    db: DBSessionDep
) -> List[ListingImageResponse]:
    return await service.upload_listing_images(db, storage, user_id, listing_id, images)


@router.delete("/listings/{listing_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing_image(
    listing_id: UUID,
    image_id: UUID,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep,
    db: DBSessionDep
):
    await service.delete_listing_image(db, storage, user_id, listing_id, image_id)


@router.get("/listings/{listing_id}/images/primary")
async def get_listing_images_primary(
    listing_id: UUID,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep,
    db: DBSessionDep
) -> ListingImageResponse:
    return await service.get_listing_images_primary(db, storage, user_id, listing_id)


@router.post("/listings/{listing_id}/images/{image_id}/primary")
async def make_listing_images_primary(
    listing_id: UUID,
    image_id: UUID,
    user_id: CurrentUserIdPanicDep,
    storage: StorageAdapterDep,
    db: DBSessionDep
) -> List[ListingImageResponse]:
    return await service.make_listing_images_primary(db, storage, user_id, listing_id, image_id)
