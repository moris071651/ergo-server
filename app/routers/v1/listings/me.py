from typing import List
from fastapi import APIRouter, Depends, Request, status
from uuid import UUID
from app.db.session import get_db, Session
from app.exceptions.auth import UserNotLoggedInException
from app.schemas.listings import ListingCreate, ListingResponseOwner, ListingUpdate


router = APIRouter(prefix="/workers/me/listings")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_listing(
    req: Request,
    data: ListingCreate,
    db=Depends(get_db)
) -> ListingResponseOwner:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.create_listing(db, user_id, data)


@router.get("/")
async def get_my_listings(
    req: Request,
    db=Depends(get_db)
) -> List[ListingResponseOwner]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_my_listings(db, user_id)


@router.get("/{listing_id}")
async def get_my_listing_by_id(
    req: Request,
    listing_id: UUID,
    db: Session = Depends(get_db)
) -> ListingResponseOwner:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_my_listing_by_id(db, user_id, listing_id)
