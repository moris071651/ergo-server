
from fastapi import APIRouter


router = APIRouter(prefix='/users/me/address', tags=["Current user's addresses"])


@router.get('/')
async def get_all_addresses():
    pass


@router.get('/{address_id}')
async def get_addresses_by_id():
    pass


@router.post()
async def add_address():
    pass


@router.patch()
async def update_address():
    pass


@router.delete()
async def remove_address():
    pass
