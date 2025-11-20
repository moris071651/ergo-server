from datetime import datetime
from sqlalchemy.orm import relationship
from app.models.worker_skill_table import worker_skill_table
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String
from app.db.session import Base


class Worker(Base):
    __tablename__ = "workers"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    bio = Column(String, nullable=True)
    service_radius_km = Column(Integer, nullable=True)
    experience_years = Column(Integer, nullable=True)

    available = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    skills = relationship(
        "Skill",
        secondary=worker_skill_table,
        lazy="joined"
    )
