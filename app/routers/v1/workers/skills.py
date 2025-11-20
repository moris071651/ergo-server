from typing import List, Union
from fastapi import APIRouter, Body, Depends, Query, Request, status

from app.db.session import Session, get_db
from app.services.workers import skills as service
from app.exceptions.auth import UserNotLoggedInException


router = APIRouter(prefix='/me/skills')


@router.get('/')
async def get_skills(
    req: Request,
    db: Session = Depends(get_db)
) -> List[str]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.get_skills(db, user_id)


@router.post('/skills', status_code=status.HTTP_201_CREATED)
async def add_skills(
    req: Request,
    skills: Union[str, List[str]] = Body(),
    db: Session = Depends(get_db)
) -> List[str]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.add_skills(db, user_id, skills)


@router.put('/skills')
async def replace_skills(
    req: Request,
    skills: Union[str, List[str]] = Body(),
    db: Session = Depends(get_db)
) -> List[str]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    return await service.replace_skills(db, user_id, skills)


@router.delete('/skills/', status_code=status.HTTP_204_NO_CONTENT)
async def remove_skills(
    req: Request,
    skills: Union[str, List[str]] = Query(),
    db: Session = Depends(get_db)
) -> List[str]:
    if req.state.user_id is None:
        raise UserNotLoggedInException()

    user_id = req.state.user_id
    await service.remove_skills(db, user_id, skills)
