from uuid import UUID
from fastapi import APIRouter
from app.db.session import DBSessionDep
from app.services.users import users as service
from app.utils.storage import StorageAdapterDep


router = APIRouter(tags=['Users'])


@router.get("/")
async def get_users():
    return await service.get_users()


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db: DBSessionDep,
    storage: StorageAdapterDep,
):    
    return await service.get_user(user_id, db, storage)


@router.get("/{user_id}/picture")
async def get_user_picture(
    user_id: UUID,
    db: DBSessionDep,
    storage: StorageAdapterDep,
):    
    return await service.get_user_picture(user_id, db, storage)
