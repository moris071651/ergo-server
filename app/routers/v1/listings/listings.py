from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

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


@router.get("/listings", response_model=List[ListingResponsePublic])
async def get_listings(
    db: DBSessionDep,
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    city: Optional[str] = Query(None, description="Filter by city"),
    title: Optional[str] = Query(None, description="Filter by title"),
    limit: Optional[int] = Query(None, description="Limit the number of results"),
    category: Optional[str] = Query(None, description="Filter by category"),
):
    if limit is not None and (limit < 1 or limit > 20):
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 20")
    
    filters = {
        "min_price": min_price,
        "max_price": max_price,
        "city": city,
        "title": title,
        "category": category,
        "limit": limit
    }

    filters = {k: v for k, v in filters.items() if v is not None}
    return await service.get_listings(db, filters=filters)


@router.get("/listings/{listing_id}")
async def get_listing_by_id(
    listing_id: UUID,
    db: DBSessionDep
) -> ListingResponsePublic:
    return await service.get_listing_by_id(db, listing_id)
