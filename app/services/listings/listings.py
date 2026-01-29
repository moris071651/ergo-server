from typing import Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.db.session import Session
from app.models.address import Address
from app.models.booking import Booking
from app.models.listing import Listing
from app.models.skills import Skill
from app.models.workers import Worker
from app.schemas.listings import ListingResponsePublic
from app.utils.workers import worker_exists


async def get_listings_by_worker(
    db: Session,
    user_id: UUID
):
    if not await worker_exists(db, user_id):
        raise HTTPException(404, "Worker not found")
    
    stmt = (
        select(Listing)
        .where(Listing.owner_id == user_id)
        .where(Listing.is_active == True)
        .where(Listing.deleted_at.is_(None))
        .order_by(Listing.created_at.desc())
    )

    result = await db.execute(stmt)
    listings = result.scalars().all()

    return [ListingResponsePublic.model_validate(l) for l in listings]


async def get_listings(db: Session, filters: Optional[dict] = None):
    stmt = (
        select(Listing)
        .where(Listing.is_active == True)
        .where(Listing.deleted_at.is_(None))
        .options(
            joinedload(Listing.worker).joinedload(Worker.address),
            joinedload(Listing.bookings)
        )
    )

    stmt = (
        stmt.outerjoin(Listing.bookings)
        .group_by(Listing.id)
        .order_by(func.count(Booking.id).desc())
    )

    if filters:
        if "min_price" in filters:
            stmt = stmt.where(Listing.price >= filters["min_price"])

        if "max_price" in filters:
            stmt = stmt.where(Listing.price <= filters["max_price"])

        if "city" in filters:
            stmt = stmt.join(Listing.worker).join(Worker.address).where(Address.city.ilike(f"%{filters['city']}%"))

        if "category" in filters:
            stmt = stmt.join(Listing.worker).join(Worker.skills).where(Skill.name.ilike(f"%{filters['category']}%"))
        
        stmt = stmt.limit(filters.get("limit", 10))
        
        if "title" in filters:
            stmt = stmt.where(Listing.title == filters["title"])

        if "query" in filters:
            for word in filters["query"].split():
                stmt = stmt.where(Listing.title.ilike(f"%{word}%"))

    else:
        stmt = stmt.limit(10)

    result = await db.execute(stmt)
    listings = result.unique().scalars().all()

    return [ListingResponsePublic.model_validate(l) for l in listings]


async def get_listing_by_id(
    db: Session,
    listing_id: UUID
):
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .where(Listing.is_active == True)
        .where(Listing.deleted_at.is_(None))
    )

    result = await db.execute(stmt)
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(404, "Listing not found")
    
    return ListingResponsePublic.model_validate(listing)
