from typing import List
from fastapi import APIRouter, status
from uuid import UUID

from app.db.session import DBSessionDep
from app.services.listings import me as service
from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.schemas.listings import ListingCreate, ListingResponseOwner, ListingUpdate


router = APIRouter(prefix="/workers/me/listings")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_listing(
    data: ListingCreate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> ListingResponseOwner:
    return await service.create_listing(db, user_id, data)


@router.get("/")
async def get_my_listings(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> List[ListingResponseOwner]:
    return await service.get_my_listings(db, user_id)


@router.get("/{listing_id}")
async def get_my_listing_by_id(
    listing_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> ListingResponseOwner:
    return await service.get_my_listing_by_id(db, user_id, listing_id)


@router.patch("/{listing_id}")
async def edit_listing(
    listing_id: UUID,
    data: ListingUpdate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> ListingResponseOwner:
    return await service.edit_listing(db, user_id, listing_id, data)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    await service.delete_listing(db, user_id, listing_id)
