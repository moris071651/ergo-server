from typing import List
from uuid import UUID
from fastapi import APIRouter

from app.db.session import DBSessionDep
from app.services.listings import listings as service
from app.schemas.listings import ListingResponsePublic


router = APIRouter(tags=["Listing Management"])


@router.get("/workers/{user_id}/listings")
async def get_listings_by_worker(
    user_id: UUID,
    db: DBSessionDep
) -> List[ListingResponsePublic]:
    return await service.get_listings_by_worker(db, user_id)


@router.get("/listings")
async def get_listings(
    db: DBSessionDep
) -> List[ListingResponsePublic]:
    return await service.get_listings(db)


@router.get("/listings/{listing_id}")
async def get_listing_by_id(
    listing_id: UUID,
    db: DBSessionDep
) -> ListingResponsePublic:
    return await service.get_listing_by_id(db, listing_id)
