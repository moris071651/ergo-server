from uuid import uuid4
from sqlalchemy.orm import relationship
from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String, func
from app.schemas.bookings import BookingState
from app.db.session import Base


class BookingReason(Base):
    __tablename__ = "booking_reasons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    from_state = Column(Enum(BookingState), nullable=False)
    to_state = Column(Enum(BookingState), nullable=False)

    reason = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    bookings = relationship("Booking", back_populates="reasons")
    user = relationship("User")
