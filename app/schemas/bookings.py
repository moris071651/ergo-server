from typing import Optional
from pydantic import BaseModel, model_validator
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from app.schemas.address import PublicAddressResponse


class BookingState(str, Enum):
    CREATED = "created"
    PENDING_PAYMENT = "pending-payment"
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    CANCELED = "canceled"
    FINISHED = "finished"
    FINISH_PENDING = "finish-pending"


class BookingPaymentState(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in-progress"
    FAILED = "failed"
    PAID = "paid"


class BookingCreate(BaseModel):
    start_at: date
    end_at: date
    address_id: UUID

    @model_validator(mode="after")
    def check_dates(self):
        if (self.end_at - self.start_at).days < 0:
            raise Exception()
        
        return self
    

class BookingReasonCreate(BaseModel):
    reason: str

    @model_validator(mode="after")
    def check_reason(self):
        if len(self.reason) < 1:
            raise Exception()
        
        return self


class BookingResponseBase(BaseModel):
    id: UUID
    state: BookingState
    start_at: date
    end_at: date
    created_at: datetime
    address: PublicAddressResponse
    reason: Optional[str]

    class Config:
        from_attributes = True


class BookingResponseWorker(BaseModel):
    customer_id: UUID


class BookingResponseCustomer(BaseModel):
    worker_id: UUID
