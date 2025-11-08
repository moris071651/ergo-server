from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status
from app.db.session import Session, get_db
from app.exceptions.auth import UserNotLoggedInException
from app.services.users import address as service
from app.schemas.address import AddressCreate, AddressResponse, AddressUpdate


router = APIRouter(prefix='/me/address', tags=["Current user's addresses"])


@router.get('/')
async def get_all_addresses(
    req: Request,
    db: Session = Depends(get_db),
) -> List[AddressResponse]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_all_addresses(db, user_id)


@router.get('/{address_id}')
async def get_addresses_by_id(
    req: Request,
    address_id: UUID,
    db: Session = Depends(get_db)
) -> AddressResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_addresses_by_id(db, user_id, address_id)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_address(
    req: Request,
    address_data: AddressCreate,
    db: Session = Depends(get_db)
) -> AddressResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.add_address(db, user_id, address_data)


@router.patch('/{address_id}')
async def update_address(
    req: Request,
    address_id: UUID,
    address_data: AddressUpdate,
    db: Session = Depends(get_db)
) -> AddressResponse:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.update_address(db, user_id, address_id, address_data)


@router.delete('/{address_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_address(
    req: Request,
    address_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    await service.remove_address(db, user_id, address_id)
