from fastapi import APIRouter
from app.services.users import users as service


router = APIRouter(prefix='/users', tags=['Users'])


@router.get("/")
async def get_users():
    return await service.get_users()


@router.get("/{user_id}")
async def get_user():
    return await service.get_user()


@router.get('/{user_id}/picture')
async def get_user_picture():
    return await service.get_user_picture()
