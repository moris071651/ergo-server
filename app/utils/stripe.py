import asyncio
import math
from fastapi import HTTPException
import stripe
from app.db.session import Session

from app.models.booking import Booking
from app.models.workers import Worker
from app.schemas.bookings import BookingState


async def pay_worker_for_booking(booking: Booking, worker: Worker):
    try:
        transfer = stripe.Transfer.create(
            amount=booking.paid_amount,
            currency=booking.paid_currency,
            destination=worker.stripe_account_id,
            source_transaction=booking.charge_id,
        )

        booking.transfer_id = transfer.id

    except stripe.error.StripeError as e:
        booking.state = BookingState.ON_HOLD
        raise HTTPException(409, "Payment failed, booking on hold")


async def create_payment_intent_for_booking(
    db: Session,
    booking: Booking,
    worker: Worker,
    amount: int,
    currency: str = "EUR",
):
    try:
        return await asyncio.to_thread(
            stripe.PaymentIntent.create,
            amount=amount,
            currency=currency.lower(),
            automatic_payment_methods={"enabled": True},
            metadata={
                "booking_id": str(booking.id),
                "worker_id": str(worker.user_id),
            },
            transfer_group=f"booking:{booking.id}",
        )

    except stripe.error.StripeError:
        booking.state = BookingState.ON_HOLD
        await db.commit()
        raise HTTPException(409, "Failed to create payment")
    
    except Exception as e:
        booking.state = BookingState.ON_HOLD
        await db.commit()
        raise HTTPException(500, f"Unexpected error creating payment: {e}")

    
async def create_stripe_worker_account(email: str) -> str:
    account = stripe.Account.create(
        type="express",
        email=email,
        capabilities={
            "transfers": {"requested": True},
        },
    )
    return account.id


def calculate_price(price: int, currency: str = 'EUR') -> int:
     return math.ceil(price)
