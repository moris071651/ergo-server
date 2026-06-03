from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, field_validator

from app.schemas.users import UserResponse


class WorkerResponse(BaseModel):
    user_id: UUID
    bio: Optional[str]
    service_radius_km: Optional[int]
    experience_years: Optional[int]
    skills: List[str]
    available: bool
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("skills", mode="before")
    @classmethod
    def flatten_skills(cls, value):
        if not value:
            return []
        
        if hasattr(value[0], "name"):
            return [skill.name for skill in value]

        return value



class PopularWorkerResponse(WorkerResponse):
    profile_image_url: Optional[str] = None
    user: UserResponse

class CurrentWorkerResponse(WorkerResponse):
    stripe_account_id: Optional[str]
    charges_enabled: bool
    payouts_enabled: bool
    updated_at: datetime


class WorkerBase(BaseModel):
    bio: Optional[str] = None
    service_radius_km: Optional[int] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None

    @field_validator("skills", mode="before")
    @classmethod
    def flatten_skills(cls, value):
        if not value:
            return []
        
        if hasattr(value[0], "name"):
            return [skill.name for skill in value]

        return value


class WorkerCreate(WorkerBase):
    address_id: UUID


class WorkerUpdate(WorkerBase):
    address_id: Optional[UUID] = None
