from datetime import datetime
from pydantic import BaseModel, model_validator
from uuid import UUID
from typing import Optional


class AddressCreate(BaseModel):
    lon: float
    lat: float
    label: str


class AddressUpdate(BaseModel):
    lon: Optional[float] = None
    lat: Optional[float] = None
    label: Optional[str] = None

    @model_validator(mode="after")
    def check_lon_lat_pair(self):
        if (self.lon is None) != (self.lat is None):
            raise ValueError("Both 'lon' and 'lat' must be provided together.")
        
        return self
    

class GeoLocation(BaseModel):
    street: Optional[str]
    house_number: Optional[str]
    city: Optional[str]
    postal_code: Optional[str] = None
    country: Optional[str]


class PublicAddressResponse(BaseModel):
    id: UUID
    lon: float
    lat: float
    label: str
    street: Optional[str]
    house_number: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]

    class Config:
        from_attributes = True


class AddressResponse(PublicAddressResponse):
    updated_at: datetime
    created_at: datetime


class MainAddressUpdate(BaseModel):
    address_id: UUID
