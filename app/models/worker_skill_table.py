from sqlalchemy import Table, Column, ForeignKey
from app.db.session import Base

worker_skill_table = Table(
    "worker_skills",
    Base.metadata,
    Column("worker_id", ForeignKey("workers.user_id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
)
