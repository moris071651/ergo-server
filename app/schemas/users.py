from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    profile_image_url: Optional[str]
    first_name: str
    last_name: str


class CurrentUserResponse(UserResponse):
    created_at: datetime
    updated_at: datetime


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserPictureResponse(BaseModel):
    profile_image_url: Optional[str]
