from fastapi import APIRouter
from app.routers.v1.listings.me import router as me
from app.routers.v1.listings.listings import router as listings
from app.routers.v1.listings.bookings import router as bookings

router = APIRouter()

router.include_router(me)
router.include_router(listings)
router.include_router(bookings)
