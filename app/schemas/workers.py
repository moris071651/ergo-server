from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


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


class CurrentWorkerResponse(WorkerResponse):
    stripe_account_id: Optional[str]
    charges_enabled: bool
    payouts_enabled: bool
    updated_at: datetime


class WorkerCreate(BaseModel):
    address_id: UUID
    bio: Optional[str]
    service_radius_km: Optional[int]
    experience_years: Optional[int]
    skills: Optional[List[str]]


class WorkerUpdate(WorkerCreate):
    pass
