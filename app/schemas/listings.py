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
