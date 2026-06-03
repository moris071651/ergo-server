from app.db.session import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.worker_skill_table import worker_skill_table


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    workers = relationship(
        "Worker",
        secondary=worker_skill_table,
        back_populates="skills"
    )
    