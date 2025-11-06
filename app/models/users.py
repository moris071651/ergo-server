import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import UUID, Column, DateTime, String, func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)

    email = Column(String, index=True)
    profile_image_key = Column(String, nullable=True)
    hashed_password = Column(String)

    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
