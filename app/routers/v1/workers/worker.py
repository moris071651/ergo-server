from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.db.session import DBSessionDep
from app.schemas.workers import PopularWorkerResponse, WorkerResponse
from app.services.workers import worker as service
from app.utils.storage import StorageAdapterDep


router = APIRouter(tags=["Worker"])

@router.get('/popular')
async def get_popular_workers_profiles(
    db: DBSessionDep,
    storage: StorageAdapterDep,
    city: Optional[str] = Query(None, description="Filter by city"),
    name: Optional[str] = Query(None, description="Filter by name"),
    limit: Optional[int] = Query(None, description="Limit the number of results"),
) -> List[PopularWorkerResponse]:
    if limit is not None and (limit < 1 or limit > 20):
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 20")
    
    filters = {
        "city": city,
        "name": name,
        "limit": limit
    }

    return await service.get_popular_workers_profiles(db, storage, filters)


@router.get('/{user_id}')
async def get_worker_profile(
    user_id: UUID,
    db: DBSessionDep
) -> WorkerResponse:
    return await service.get_worker_profile(db, user_id)


@router.get('/')
async def get_all_worker_profiles(
    db: DBSessionDep,
) -> List[WorkerResponse]:
    return await service.get_all_worker_profiles(db)
