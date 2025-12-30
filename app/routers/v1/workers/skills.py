from typing import List, Union
from fastapi import APIRouter, Body, Query, status

from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.services.workers import skills as service


router = APIRouter(prefix='/me/skills')


@router.get('/')
async def get_skills(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
) -> List[str]:
    return await service.get_skills(db, user_id)


@router.post('/skills', status_code=status.HTTP_201_CREATED)
async def add_skills(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    skills: Union[str, List[str]] = Body(...)
) -> List[str]:
    return await service.add_skills(db, user_id, skills)


@router.put('/skills')
async def replace_skills(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    skills: Union[str, List[str]] = Body(...)
) -> List[str]:
    return await service.replace_skills(db, user_id, skills)


@router.delete('/skills/', status_code=status.HTTP_204_NO_CONTENT)
async def remove_skills(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    skills: Union[str, List[str]] = Query(...)
):
    await service.remove_skills(db, user_id, skills)
