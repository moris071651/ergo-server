from typing import Optional
from pydantic import BaseModel, model_validator
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from app.schemas.address import PublicAddressResponse
from app.schemas.listings import ListingResponseOwner, ListingResponsePublic


class BookingState(str, Enum):
    ON_HOLD = "on-hold"
    CREATED = "created"
    WAITING_APPROVAL = "waiting-approval"
    PENDING_PAYMENT = "pending-payment"
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    CANCELED = "canceled"
    FINISH_PENDING = "finish-pending"
    FINISHED = "finished"


class BookingPaymentState(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in-progress"
    FAILED = "failed"
    PAID = "paid"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class BookingCreate(BaseModel):
    start_at: date
    end_at: date
    address_id: UUID

    @model_validator(mode="after")
    def check_dates(self):
        if (self.end_at - self.start_at).days < 0:
            raise ValueError("end_at must be after start_at")
        
        return self
    

class BookingReasonCreate(BaseModel):
    reason: str

    @model_validator(mode="after")
    def check_reason(self):
        if len(self.reason) < 1:
            raise ValueError("reason must not be empty")
        
        return self


class BookingResponseBase(BaseModel):
    id: UUID
    state: BookingState
    start_at: date
    end_at: date
    created_at: datetime
    address: PublicAddressResponse
    reason: Optional[str] = None
    customer_id: UUID
    worker_id: UUID

    class Config:
        from_attributes = True


class BookingResponseWorker(BookingResponseBase):
    listing: ListingResponseOwner


class BookingResponseCustomer(BookingResponseBase):
    listing: ListingResponsePublic
    client_secret: str | None = None
