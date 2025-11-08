from uuid import uuid4
from sqlalchemy import UUID, Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    label = Column(String, nullable=False)

    lon = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)

    street = Column(String, nullable=True)
    city = Column(String, nullable=True)
    house_number = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"<Address {self.label} ({self.city}, {self.country})>"
