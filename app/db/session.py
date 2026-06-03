from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import DATABASE_ECHO, DATABASE_FUTURE, DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=DATABASE_ECHO, future=DATABASE_FUTURE)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
Session = AsyncSession


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()

        except:
            await session.rollback()
            raise


DBSessionDep = Annotated[
    AsyncSession,
    Depends(get_db)
]