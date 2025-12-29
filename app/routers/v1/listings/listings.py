from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from app.db.session import Session, get_db

from app.schemas.listings import ListingResponsePublic


router = APIRouter()


@router.get("/workers/{user_id}/listings")
async def get_listings_by_worker(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> List[ListingResponsePublic]:
    return await service.get_listings_by_worker(db, user_id)


@router.get("/listings")
async def get_listings(
    db: Session = Depends(get_db)
) -> List[ListingResponsePublic]:
    return await service.get_listings(db)


@router.get("/listings/{listing_id}")
async def get_listing_by_id(
    listing_id: UUID,
    db: Session = Depends(get_db)
) -> ListingResponsePublic:
    return await service.get_listing_by_id(db, listing_id)
