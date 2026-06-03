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
    experience_years = Column(Integer, nullable=True)

    service_radius_km = Column(Integer, nullable=True)
    address_id = Column(
        UUID(as_uuid=True),
        ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
    )

    stripe_account_id = Column(String, nullable=True)
    charges_enabled = Column(Boolean, default=False)
    payouts_enabled = Column(Boolean, default=False)
    
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
    address = relationship(
        "Address",
        lazy="joined",
        uselist=False
    )
    user = relationship("User", lazy="joined")
    bookings = relationship("Booking", back_populates="worker")
    listings = relationship("Listing", back_populates="worker")
