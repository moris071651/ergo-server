from uuid import UUID
from fastapi import APIRouter, Depends
from app.db.session import Session, get_db
from app.services.users import users as service
from app.utils.storage import get_storage_adapter
from app.utils.storage.base import StorageAdapter


router = APIRouter(tags=['Users'])


@router.get("/")
async def get_users():
    return await service.get_users()


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    storage: StorageAdapter = Depends(get_storage_adapter)
):    
    return await service.get_user(user_id, db, storage)


@router.get("/{user_id}/picture")
async def get_user_picture(
    user_id: UUID,
    db: Session = Depends(get_db),
    storage: StorageAdapter = Depends(get_storage_adapter)
):    
    return await service.get_user_picture(user_id, db, storage)
