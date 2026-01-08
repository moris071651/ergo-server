from uuid import uuid4
from sqlalchemy import UUID, Column, Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.schemas.bookings import BookingPaymentState, BookingState


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.user_id"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)

    start_at = Column(Date(), nullable=False)
    end_at = Column(Date(), nullable=False)

    state = Column(Enum(BookingState), nullable=False, default=BookingState.CREATED)
    payment_state = Column(Enum(BookingPaymentState), nullable=False, default=BookingPaymentState.CREATED)

    transfer_id = Column(String, nullable=True)
    payment_intent_id = Column(String(64), nullable=True, index=True)
    charge_id = Column(String, nullable=True, index=True)
    paid_currency = Column(String(3), nullable=True)
    paid_amount = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    listing = relationship("Listing", back_populates="bookings")
    worker = relationship("Worker", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
    address = relationship("Address", back_populates="bookings")
    reasons = relationship("BookingReason", back_populates="bookings")
