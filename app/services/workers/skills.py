from typing import List, Optional, Union
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.skills import Skill
from app.models.workers import Worker
from app.utils.workers import get_worker_panic


async def _normalize_skills(skills: Union[str, List[str]]) -> List[str]:
    if isinstance(skills, str):
        skills = [skills]

    return [s.strip().lower() for s in skills if s.strip()]


async def get_skills(db: AsyncSession, user_id: UUID):
    worker = await get_worker_panic(db, user_id)
    return [skill.name for skill in worker.skills]


async def add_skills(db: AsyncSession, user_id: UUID, skills: Union[str, List[str]], worker: Optional[Worker] = None):
    skill_names = await _normalize_skills(skills)

    if worker is None:
        worker = await get_worker_panic(db, user_id)

    stmt = select(Skill).where(Skill.name.in_(skill_names))
    result = await db.execute(stmt)
    existing_skills = result.scalars().all()
    existing_names = {s.name for s in existing_skills}

    invalid_skills = set(skill_names) - existing_names
    if invalid_skills:
        raise Exception(f"Invalid skills: {', '.join(invalid_skills)}")

    current_worker_skill_names = {s.name for s in worker.skills}
    for skill in existing_skills:
        if skill.name not in current_worker_skill_names:
            worker.skills.append(skill)

    await db.commit()
    await db.refresh(worker)
    return [s.name for s in worker.skills]


async def replace_skills(db: AsyncSession, user_id: UUID, skills: Union[str, List[str]]):
    skill_names = await _normalize_skills(skills)
    worker = await get_worker_panic(db, user_id)

    worker.skills = []
    await db.commit()

    return await add_skills(db, user_id, skill_names)
