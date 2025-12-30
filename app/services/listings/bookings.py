from datetime import datetime
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from app.db.session import Session
from app.models.address import Address
from app.models.booking import Booking
from app.models.booking_reason import BookingReason
from app.models.listing import Listing
from app.schemas.bookings import BookingCreate, BookingReasonCreate, BookingResponseCustomer, BookingResponseWorker, BookingState


async def _get_owned_booking(db: Session, booking_id: UUID, worker_id: UUID):
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.worker_id == worker_id)
    )

    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    return booking


async def _get_customer_booking(db: Session, booking_id: UUID, user_id: UUID):
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.customer_id == user_id)
    )

    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    return booking


async def _add_reason(db: Session, booking: Booking, user_id: UUID, from_state: BookingState, to_state: BookingState, reason: str):
    entry = BookingReason(
        booking_id=booking.id,
        user_id=user_id,
        from_state=from_state,
        to_state=to_state,
        reason=reason
    )

    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    booking.reason = entry.reason


async def _append_reason(db: Session, booking: Booking):
    stmt = (
        select(BookingReason)
        .where(BookingReason.booking_id == booking.id)
        .order_by(BookingReason.created_at.desc())
    )

    result = await db.execute(stmt)
    entry = result.scalars().first()

    if entry:
        booking.reason = entry.reason


async def create_booking(db: Session, user_id: UUID, listing_id: UUID, data: BookingCreate):
    stmt = select(Listing).where(Listing.id == listing_id, Listing.is_active == True)
    result = await db.execute(stmt)
    listing = result.scalars().first()

    if not listing:
        raise HTTPException(404, "Listing not found")
    
    if listing.owner_id == user_id:
        raise HTTPException(400, "You cannot book your own listing")
    
    stmt = select(Address).where(Address.id == data.address_id, Address.user_id == user_id)
    result = await db.execute(stmt)
    address = result.scalars().first()
    if not address:
        raise HTTPException(404, "Address not found")

    stmt = (
        select(Booking)
        .where(Booking.customer_id == user_id)
        .where(Booking.worker_id == listing.owner_id)
        .where(Booking.address_id == data.address_id)
        .where(~Booking.state.in_([BookingState.FINISHED]))
    )
    result = await db.execute(stmt)
    old_booking = result.scalars().first()
    if old_booking:
        raise HTTPException(400, "You already have an active booking with this worker at this address")

    requested_days = (data.end_at - data.start_at).days + 1
    if requested_days < listing.duration_days:
        raise Exception(f"Booking must be at least {listing.duration_days} day(s)")

    booking = Booking(
        listing_id=listing_id,
        customer_id=user_id,
        worker_id=listing.owner_id,
        address_id=address.id,
        start_at=data.start_at,
        end_at=data.end_at,
        state=BookingState.PENDING,
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    return BookingResponseCustomer.model_validate(booking)


async def list_worker_bookings(db: Session, worker_id: UUID, status_filter):
    stmt = (
        select(Booking)
        .where(Booking.worker_id == worker_id)
        .order_by(Booking.start_at.desc())
    )

    if status_filter:
        stmt = stmt.where(Booking.state == status_filter)

    result = await db.execute(stmt)
    bookings = result.scalars().all()

    for b in bookings:
        await _append_reason(db, b)

    return [BookingResponseWorker.model_validate(b) for b in bookings]


async def list_customer_bookings(db: Session, user_id: UUID, status_filter):
    stmt = (
        select(Booking)
        .where(Booking.customer_id == user_id)
        .order_by(Booking.start_at.desc())
    )
    
    if status_filter:
        stmt = stmt.where(Booking.state == status_filter)

    result = await db.execute(stmt)
    bookings = result.scalars().all()

    for b in bookings:
        await _append_reason(db, b)

    return [BookingResponseCustomer.model_validate(b) for b in bookings]


async def get_worker_booking_by_id(db: Session, worker_id: UUID, booking_id: UUID):
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.worker_id == worker_id)
    )

    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(404, "Booking not found")
    
    await _append_reason(db, booking)
    return BookingResponseWorker.model_validate(booking)


async def get_customer_booking_by_id(db: Session, user_id: UUID, booking_id: UUID):
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where(Booking.customer_id == user_id)
    )

    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    await _append_reason(db, booking)
    return BookingResponseCustomer.model_validate(booking)


async def worker_confirm_booking(db: Session, user_id: UUID, booking_id: UUID):
    booking = await _get_owned_booking(db, booking_id, user_id)

    if booking.state != BookingState.PENDING:
        raise HTTPException(400, "Only pending bookings can be confirmed")

    booking.state = BookingState.IN_PROGRESS
    booking.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    return BookingResponseWorker.model_validate(booking)


# TODO fix this thing
async def cancel_booking(db: Session, user_id: UUID, booking_id: UUID):
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .where((Booking.customer_id == user_id) | (Booking.worker_id == user_id))
    )

    result = await db.execute(stmt)
    booking = result.scalars().first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    if booking.state != BookingState.PENDING:
        raise HTTPException(400, "Cannot cancel booking at this stage")

    booking.state = BookingState.CANCELED
    booking.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(booking)

    if user_id == booking.worker_id:
        return BookingResponseWorker.model_validate(booking)
    
    else:
        return BookingResponseCustomer.model_validate(booking)


async def worker_finish_booking(db: Session, user_id: UUID, booking_id: UUID, data: BookingReasonCreate):
    booking = await _get_owned_booking(db, booking_id, user_id)

    if booking.state != BookingState.IN_PROGRESS:
        raise HTTPException(400, "Booking must be in-progress to finish")
    
    state = booking.state
    booking.state = BookingState.FINISHED_PENDING
    booking.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    await _add_reason(db, booking, user_id, state, booking.state, data.reason)
    return BookingResponseWorker.model_validate(booking)


async def customer_confirm_finish(db: Session, user_id: UUID, booking_id: UUID, data: BookingReasonCreate):
    booking = await _get_customer_booking(db, booking_id, user_id)

    if booking.state != BookingState.FINISHED_PENDING:
        raise HTTPException(400, "Booking is not awaiting confirmation")

    state = booking.state
    booking.state = BookingState.FINISHED
    booking.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    await _add_reason(db, booking, user_id, state, booking.state, data.reason)
    return BookingResponseCustomer.model_validate(booking)


async def customer_deny_finish(db: Session, user_id: UUID, booking_id: UUID, data: BookingReasonCreate):
    booking = await _get_customer_booking(db, booking_id, user_id)

    if booking.state != BookingState.FINISHED_PENDING:
        raise HTTPException(400, "Booking not awaiting confirmation")

    state = booking.state
    booking.state = BookingState.IN_PROGRESS
    booking.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    await _add_reason(db, booking, user_id, state, booking.state, data.reason)
    return BookingResponseCustomer.model_validate(booking)
