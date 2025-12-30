from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy import select
import stripe

from app.config.settings import STRIPE_WEBHOOK_SECRET
from app.db.session import Session, get_db
from app.models.booking import Booking
from app.models.workers import Worker
from app.schemas.bookings import BookingPaymentState, BookingState
from app.utils.workers import get_worker_panic


router = APIRouter(prefix='/stripe', tags=['Stripe'])


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=STRIPE_WEBHOOK_SECRET,
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    
    except Exception:
        raise HTTPException(400, "Invalid payload")

    event_type = event["type"]
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]

        payment_intent_id = session.get("payment_intent")
        booking_id = session["metadata"].get("booking_id")

        if not booking_id or not payment_intent_id:
            return {"status": "ignored"}
        
        stmt = (select(Booking).where(Booking.id == booking_id))
        result = await db.execute(stmt)
        booking = result.scalars().first()

        if not booking:
            return {"status": "ignored"}

        if booking.status != BookingState.CREATED:
            return {"status": "already_processed"}

        booking.payment_intent_id = payment_intent_id
        booking.state = BookingState.PENDING_PAYMENT
        booking.payment_state = BookingPaymentState.IN_PROGRESS

        await db.commit()

    elif event_type == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]

        stmt = (select(Booking).where(Booking.payment_intent_id == payment_intent_id))
        result = await db.execute(stmt)
        booking = result.scalars().first()

        if not booking:
            return {"status": "ignored"}
        
        if booking.status != BookingState.PENDING_PAYMENT:
            return {"status": "already_processed"}

        if booking.payment_state in (BookingPaymentState.PAID, BookingPaymentState.FAILED):
            return {"status": "already_processed"}

        booking.status = BookingState.PENDING
        booking.payment_state = BookingPaymentState.PAID
        booking.paid_amount = payment_intent["amount_received"]
        booking.paid_currency = payment_intent["currency"]

        await db.commit()

    elif event_type == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]

        stmt = (select(Booking).where(Booking.payment_intent_id == payment_intent["id"]))
        result = await db.execute(stmt)
        booking = result.scalars().first()
            
        if not booking:
            return {"status": "ignored"}

        if booking.status != BookingState.PENDING_PAYMENT:
            return {"status": "already_processed"}
        
        if booking.payment_state not in [BookingPaymentState.CREATED, BookingPaymentState.IN_PROGRESS]:
            return {"status": "already_processed"}

        booking.status = BookingState.CANCELED
        booking.payment_state = BookingPaymentState.FAILED
        await db.commit()

    elif event_type == "charge.refunded":
        charge = event["data"]["object"]

        booking = await _find_booking_by_payment_intent(charge["payment_intent"])
        if not booking:
            return {"status": "ignored"}

        booking.payment_state = BookingPaymentState.REFUNDED
        booking.status = BookingState.CANCELED
        await db.commit()

    elif event["type"] == "account.updated":
        account = event["data"]["object"]
        worker = _find_by_stripe_account_id(account["id"])

        worker.charges_enabled = account["charges_enabled"]
        worker.payouts_enabled = account["payouts_enabled"]


    return {"status": "ok"}



STRIPE_REFRESH_URL = "https://yourapp.com/stripe/onboarding/refresh"
STRIPE_RETURN_URL = "https://yourapp.com/stripe/onboarding/complete"

@router.post("/onboarding")
async def stripe_onboarding(
    db: Session,
    user_id: UUID
):
    worker = await get_worker_panic(db, user_id)
    if not worker.stripe_account_id:
        raise HTTPException(400, "Worker has no Stripe account")

    account_link = stripe.AccountLink.create(
        account=worker.stripe_account_id,
        refresh_url=STRIPE_REFRESH_URL,
        return_url=STRIPE_RETURN_URL,
        type="account_onboarding",
    )

    return {
        "url": account_link.url
    }
