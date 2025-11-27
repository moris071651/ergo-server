from uuid import UUID
from fastapi import APIRouter, Depends, Request
from app.db.session import Session, get_db
from app.exceptions.auth import UserNotLoggedInException

from app.services.workers import address as service
from app.schemas.address import AddressResponse, MainAddressUpdate


router_me = APIRouter(prefix='/me/address')
router_global = APIRouter(prefix='/{user_id}/address')


@router_me.get('/')
async def get_my_main_address(
    req: Request,
    db: Session = Depends(get_db)
) -> AddressResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_my_main_address(db, user_id)


@router_me.put('/')
async def update_my_main_address(
    req: Request,
    data: MainAddressUpdate,
    db: Session = Depends(get_db)
) -> AddressResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.update_my_main_address(db, user_id, data)


@router_global.get('/')
async def get_worker_main_address(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> AddressResponse:
    return await service.get_worker_main_address(db, user_id)


router = APIRouter()
router.include_router(router_me)
router.include_router(router_global)
