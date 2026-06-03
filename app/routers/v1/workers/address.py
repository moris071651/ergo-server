from uuid import UUID
from fastapi import APIRouter
from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep

from app.services.workers import address as service
from app.schemas.address import AddressResponse, MainAddressUpdate


router_me = APIRouter(prefix='/me/address', tags=["Worker's addresses"])
router_global = APIRouter(prefix='/{user_id}/address', tags=["Worker's addresses"])


@router_me.get('/')
async def get_my_main_address(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> AddressResponse:
    return await service.get_my_main_address(db, user_id)


@router_me.put('/')
async def update_my_main_address(
    data: MainAddressUpdate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> AddressResponse:
    return await service.update_my_main_address(db, user_id, data)


@router_global.get('/')
async def get_worker_main_address(
    user_id: UUID,
    db: DBSessionDep
) -> AddressResponse:
    return await service.get_worker_main_address(db, user_id)


router = APIRouter()
router.include_router(router_me)
router.include_router(router_global)
