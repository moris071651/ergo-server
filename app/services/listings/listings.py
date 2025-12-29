from uuid import UUID
from sqlalchemy import select

from app.db.session import Session
from app.models.listing import Listing
from app.schemas.listings import ListingResponsePublic
from app.utils.workers import worker_exists


async def get_listings_by_worker(
    db: Session,
    user_id: UUID
):
    if not await worker_exists(db, user_id):
        raise Exception()

    
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
