from typing import List
from uuid import UUID
from fastapi import APIRouter, status
from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.services.users import address as service
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate


router = APIRouter(prefix='/me/address', tags=["Current user's addresses"])


@router.get('/')
async def get_all_addresses(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> List[AddressResponse]:
    return await service.get_all_addresses(db, user_id)


@router.get('/{address_id}')
async def get_addresses_by_id(
    address_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> AddressResponse:
    return await service.get_addresses_by_id(db, user_id, address_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_address(
    address_data: AddressCreate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> AddressResponse:
    return await service.add_address(db, user_id, address_data)


@router.patch('/{address_id}')
async def update_address(
    address_id: UUID,
    address_data: AddressUpdate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> AddressResponse:
    return await service.update_address(db, user_id, address_id, address_data)


@router.delete('/{address_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_address(
    address_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> None:
    await service.remove_address(db, user_id, address_id)
