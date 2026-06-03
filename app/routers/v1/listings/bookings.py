from typing import List, Optional
from fastapi import APIRouter, Query, status
from uuid import UUID

from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.services.listings import bookings as service
from app.schemas.bookings import BookingCreate, BookingResponseCustomer, BookingResponseWorker, BookingState


router = APIRouter(tags=["Bookings"])


@router.post("/listings/{listing_id}/book", status_code=status.HTTP_201_CREATED)
async def create_booking(
    listing_id: UUID,
    data: BookingCreate,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> BookingResponseCustomer:
    return await service.create_booking(db, user_id, listing_id, data)


@router.post("/bookings/{booking_id}/reject")
async def reject_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.reject_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/approve")
async def approve_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.approve_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/start")
async def start_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.start_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/finish")
async def finish_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.finish_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/finish/confirm")
async def confirm_finish_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.confirm_finish_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/finish/deny")
async def deny_finish_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.deny_finish_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    return await service.cancel_booking(db, user_id, booking_id)


@router.get("/workers/me/bookings")
async def list_worker_bookings(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    status_filter: Optional[BookingState] = Query(None, description="pending,in-progress,canceled,finished")
) -> List[BookingResponseWorker]:
    return await service.list_worker_bookings(db, user_id, status_filter)


@router.get("/workers/me/bookings/{booking_id}")
async def get_worker_booking_by_id(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> BookingResponseWorker:
    return await service.get_worker_booking_by_id(db, user_id, booking_id)


@router.get("/users/me/bookings")
async def list_customer_bookings(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep,
    status_filter: Optional[BookingState] = Query(None, description="pending,in-progress,canceled,finished")
) -> List[BookingResponseCustomer]:
    return await service.list_customer_bookings(db, user_id, status_filter)


@router.get("/users/me/bookings/{booking_id}")
async def get_customer_booking_by_id(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> BookingResponseCustomer:
    return await service.get_customer_booking_by_id(db, user_id, booking_id)

@router.get("/bookings12/{booking_id}")
async def get_booking12_by_id(
    booking_id: UUID,
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
) -> BookingResponseCustomer:
    return await service.get_booking12_by_id(db, user_id, booking_id)
