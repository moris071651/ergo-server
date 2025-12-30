from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from app.db.session import Session, get_db
from app.schemas.bookings import BookingCreate, BookingResponseCustomer, BookingResponseWorker

router = APIRouter(tags=["Bookings"])


@router.post("/listings/{listing_id}/book", status_code=status.HTTP_201_CREATED)
async def create_booking(
    listing_id: UUID,
    data: BookingCreate,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseCustomer:
    return await service.create_booking(db, user_id, listing_id, data)


@router.get("/workers/me/bookings")
async def list_worker_bookings(
    status_filter: Optional[BookingState] = Query(None, description="pending,in-progress,canceled,finished"),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> List[BookingResponseWorker]:
    return await service.list_worker_bookings(db, user_id, status_filter)


@router.get("/workers/me/bookings/{booking_id}")
async def get_worker_booking_by_id(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseWorker:
    return await service.get_worker_booking_by_id(db, user_id, booking_id)


@router.get("/users/me/bookings")
async def list_customer_bookings(
    status_filter: Optional[BookingState] = Query(None, description="pending,in-progress,canceled,finished"),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> List[BookingResponseCustomer]:
    return await service.list_customer_bookings(db, user_id, status_filter)


@router.get("/users/me/bookings/{booking_id}")
async def get_customer_booking_by_id(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseCustomer:
    return await service.get_customer_booking_by_id(db, user_id, booking_id)


@router.post("/workers/me/bookings/{booking_id}/confirm")
async def worker_confirm_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseWorker:
    return await service.worker_confirm_booking(db, user_id, booking_id)


@router.post("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseWorker:
    return await service.cancel_booking(db, user_id, booking_id)


@router.post("/workers/me/bookings/{booking_id}/finish")
async def worker_finish_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseWorker:
    return await service.worker_finish_booking(db, user_id, booking_id)


@router.post("/users/me/bookings/{booking_id}/finish/confirm")
async def customer_confirm_finish(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseCustomer:
    return await service.customer_confirm_finish(db, user_id, booking_id)


@router.post("/users/me/bookings/{booking_id}/finish/deny")
async def customer_deny_finish(
    booking_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> BookingResponseCustomer:
    return await service.customer_deny_finish(db, user_id, booking_id)
