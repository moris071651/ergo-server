from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.session import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workers.user_id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(120), nullable=False)
    description = Column(String, nullable=True)

    price_cents = Column(Integer, nullable=False)
    currency_iso_code = Column(String(3), nullable=False)

    allow_recurring = Column(Boolean, default=True)
    visit_required = Column(Boolean, default=True)

    duration_days = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), default=None ,nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("Worker", back_populates="listings")
    bookings = relationship("Booking", back_populates="listing")

    images = relationship(
        "ListingImage",
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="ListingImage.sort_order"
    )
