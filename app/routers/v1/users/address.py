
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from app.db.session import Session, get_db
from app.exceptions.auth import UserNotLoggedInException
from app.services.users import address as service
from app.schemas.address import AddressResponse


router = APIRouter(prefix='/users/me/address', tags=["Current user's addresses"])


@router.get('/')
async def get_all_addresses(
    req: Request,
    db: Session = Depends(get_db),
) -> List[AddressResponse]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_all_addresses(db, user_id)

