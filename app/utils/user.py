from uuid import UUID
from sqlalchemy import exists, select

from app.db.session import Session
from app.models.users import User


async def user_exists(db: Session, user_id: UUID):
    stmt = select(exists().where(User.id == user_id, User.deleted_at.is_(None)))
    result = await db.execute(stmt)
    return result.scalar()


async def email_available(db: Session, email: str):
    stmt = select(exists().where(User.email == email, User.deleted_at.is_(None)))
    result = await db.execute(stmt)
    return not result.scalar()
