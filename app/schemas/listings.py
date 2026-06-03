from pydantic_extra_types.currency_code import Currency
from pydantic import BaseModel, model_validator
from uuid import UUID
from currencies import Currency as CurrencyFormatter
from datetime import datetime


class ListingCreate(BaseModel):
    title: str
    description: str | None = None
    price_cents: int
    currency_iso_code: Currency = "EUR"
    allow_recurring: bool = False
    visit_required: bool = False
    duration_days: int | None = None

    @model_validator(mode="after")
    def check_price(self):
        if self.price_cents is not None and self.price_cents < 0:
            raise ValueError("The price could not be negative.")
        
        return self
    
    @model_validator(mode="after")
    def check_duration(self):
        if self.duration_days is not None and self.duration_days < 1:
            raise ValueError("The duration_days could not be less then 1.")
        
        return self


class ListingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None
    price_cents: int | None = None
    currency_iso_code: Currency | None = None
    allow_recurring: bool | None = None
    duration_days: int | None = None
    visit_required: bool | None = None

    @model_validator(mode="after")
    def check_price(self):
        if self.price_cents is not None and self.price_cents < 0:
            raise ValueError("The price could not be negative.")
        
        return self
    
    @model_validator(mode="after")
    def check_duration(self):
        if self.duration_days is not None and self.duration_days < 1:
            raise ValueError("The duration_days could not be less then 1.")
        
        return self


class ListingResponsePublic(BaseModel):
    id: UUID
    owner_id: UUID

    title: str
    description: str | None

    price_cents: int
    currency_iso_code: Currency
    price_str: str | None = None

    allow_recurring: bool = False
    visit_required: bool = False

    duration_days: int
    created_at: datetime

    @model_validator(mode="after")
    def fill_price_str(self):
        if self.price_str is None:
            formatter = CurrencyFormatter(str(self.currency_iso_code))
            self.price_str = formatter.get_money_format(self.price_cents / 100)
        
        return self

    class Config:
        from_attributes = True

    
class ListingResponseOwner(ListingResponsePublic):
    updated_at: datetime
    is_active: bool


class ListingImageResponse(BaseModel):
    id: UUID
    url: str
    is_primary: bool
    sort_order: int

    class Config:
        from_attributes = True
