from typing import Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut

from app.schemas.address import GeoLocation


geolocator = Nominatim(user_agent="ergo-server")

def reverse_geocode(lat: float, lon: float) -> Optional[GeoLocation]:
    try:
        location = geolocator.reverse((lat, lon), language="en", addressdetails=True)
        if not location:
            return {}

        addr = location.raw.get("address", {})

        street = addr.get("road")
        house_number = addr.get("house_number")
        city = addr.get("city") or addr.get("town") or addr.get("village")
        postal_code = addr.get("postcode")
        country = addr.get("country")

        return GeoLocation(
            street=street,
            house_number=house_number,
            city=city,
            postal_code=postal_code,
            country=country
        )

    except (GeocoderTimedOut, GeocoderServiceError):
        return None
