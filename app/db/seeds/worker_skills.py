from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.skills import Skill


DEFAULT_SKILLS = [
    "plumber", "painter", "electrician", "carpenter", "mason",
    "roofer", "drywaller", "welder", "locksmith", "landscaper",
    "glazier", "hvac technician", "tile setter", "flooring installer",
    "demolition worker", "concrete finisher", "insulation installer",
    "ironworker", "scaffolder", "appliance installer"
]


async def seed_worker_skills(db: AsyncSession):
    stmt = select(Skill)
    result = await db.execute(stmt)
    exists = result.scalars().first()

    if not exists:
        new_skills = [Skill(name=name) for name in DEFAULT_SKILLS]
        db.add_all(new_skills)
        await db.commit()
        print("Successfully seeded default skills!")

    else:
        print("Skills table already has data. Skipping seed.")
