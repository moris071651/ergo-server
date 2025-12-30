from uuid import UUID
from typing import List
from sqlalchemy import select
from datetime import datetime

from app.db.session import Session
from app.models.listing import Listing
from app.schemas.listings import ListingCreate, ListingUpdate, ListingResponseOwner


async def create_offering(
    db: Session,
    user_id: UUID,
    data: ListingCreate
) -> ListingResponseOwner:
    listing = Listing(
        worker_id=user_id,
        title=data.title,
        description=data.description,
        price_cents=data.price_cents,
        currency_iso_code=str(data.currency_iso_code),
        allow_recurring=data.allow_recurring,
        visit_required=data.visit_required,
        duration_days=data.duration_days
    )

    db.add(listing)
    await db.commit()

    await db.refresh(listing)
    return ListingResponseOwner.model_validate(listing)


async def get_my_listings(
    db: Session,
    user_id: UUID
) -> List[ListingResponseOwner]:
    stmt = (
        select(Listing)
        .where(Listing.owner_id == user_id)
        .where(Listing.deleted_at.is_(None))
        .order_by(Listing.created_at.desc())
    )

    result = await db.execute(stmt)
    listings = result.scalars().all()

    return [ListingResponseOwner.model_validate(l) for l in listings]


async def get_my_listing_by_id(
    db: Session,
    user_id: UUID,
    listing_id: UUID
) -> ListingResponseOwner:
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .where(Listing.owner_id == user_id)
        .where(Listing.deleted_at.is_(None))
    )

    result = await db.execute(stmt)
    listing = result.scalars().first()

    if not listing:
        raise Exception()

    return ListingResponseOwner.model_validate(listing)


async def edit_listing(
    db: Session,
    user_id: UUID,
    listing_id: UUID,
    data: ListingUpdate
) -> ListingResponseOwner:
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .where(Listing.owner_id == user_id)
        .where(Listing.deleted_at.is_(None))
    )

    result = await db.execute(stmt)
    listing = result.scalars().first()

    if not listing:
        raise Exception()

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, key, value)

    listing.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(listing)

    return ListingResponseOwner.model_validate(listing)


async def delete_listing(
    db: Session,
    user_id: UUID,
    listing_id: UUID
):
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id)
        .where(Listing.owner_id == user_id)
        .where(Listing.deleted_at.is_(None))
    )

    result = await db.execute(stmt)
    listing = result.scalars().first()

    if not listing:
        raise Exception()

    listing.deleted_at = datetime.utcnow()
    await db.commit()
