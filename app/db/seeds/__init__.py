from app.db.seeds.worker_skills import seed_worker_skills
from app.db.session import get_db


async def init_seeds():
    async for db in get_db():
        await seed_worker_skills(db)
