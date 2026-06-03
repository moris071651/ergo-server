from fastapi import APIRouter, HTTPException, Header, Request, status
from sqlalchemy import select
import stripe

from app.config.settings import STRIPE_WEBHOOK_SECRET
from app.db.session import DBSessionDep
from app.middlewares.user_verify import CurrentUserIdPanicDep
from app.models.booking import Booking
from app.models.workers import Worker
from app.schemas.bookings import BookingPaymentState, BookingState
from app.utils.webhook import acquire_event_lock
from app.utils.workers import get_worker_panic

STRIPE_REFRESH_URL = "https://yourapp.com/stripe/onboarding/refresh"
STRIPE_RETURN_URL = "https://yourapp.com/stripe/onboarding/complete"

router = APIRouter(prefix='/stripe', tags=['Stripe'])


async def _find_booking_by_id(db, booking_id):
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
    )

    result = await db.execute(stmt)
    return result.scalars().first()


async def _find_booking_by_payment_intent(db, payment_intent_id):
    stmt = (
        select(Booking)
        .where(Booking.payment_intent_id == payment_intent_id)
    )

    result = await db.execute(stmt)
    return result.scalars().first()


async def _find_booking_by_charge_id(db, charge_id):
    stmt = (
        select(Booking)
        .where(Booking.charge_id == charge_id)
    )

    result = await db.execute(stmt)
    return result.scalars().first()


async def _find_worker_by_stripe_account_id(db, stripe_account_id):
    stmt = (
        select(Worker)
        .where(Worker.stripe_account_id == stripe_account_id)
    )

    result = await db.execute(stmt)
    return result.scalars().first()


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(
    request: Request,
    db: DBSessionDep,
    stripe_signature: str = Header(..., alias="Stripe-Signature")
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
    
    if not await acquire_event_lock(event["id"]):
        return {"status": "duplicate"}
        
    match event["type"]:
        case "checkout.session.completed": return await handle_checkout_session_completed(db, event)
        case "payment_intent.succeeded": return await handle_payment_intent_succeeded(db, event)
        case "payment_intent.payment_failed": return await handle_payment_intent_failed(db, event)
        case "charge.refunded": return await handle_charge_refunded(db, event)
        case "checkout.session.expired": return await handle_checkout_session_expired(db, event)
        case "payment_intent.canceled": return await handle_payment_intent_canceled(db, event)
        case "charge.dispute.created": return await handle_charge_dispute_created(db, event)
        case "account.updated": return await handle_account_updated(db, event)
        case "account.application.deauthorized": return await handle_account_application_deauthorized(db, event)
        case _: return {"status": "unhandled"}


async def handle_checkout_session_completed(db, ev):
    session = ev["data"]["object"]

    payment_intent_id = session.get("payment_intent")
    booking_id = session["metadata"].get("booking_id")

    if not booking_id or not payment_intent_id:
        return {"status": "ignored"}
    
    booking = await _find_booking_by_id(db, booking_id)

    if not booking:
        return {"status": "ignored"}

    booking.payment_intent_id = payment_intent_id

    await db.commit()
    return {"status": "ok"}


async def handle_payment_intent_succeeded(db, ev):
    payment_intent = ev["data"]["object"]
    payment_intent_id = payment_intent["id"]

    booking = await _find_booking_by_payment_intent(db, payment_intent_id)

    if not booking:
        return {"status": "ignored"}
    
    if booking.state != BookingState.PENDING_PAYMENT:
        return {"status": "already_processed"}
    
    if booking.payment_state == BookingPaymentState.CREATED:
        return {"status": "ignored"}

    if booking.payment_state != BookingPaymentState.IN_PROGRESS:
        return {"status": "already_processed"}
    
    print(payment_intent)
    
    charges = payment_intent.get("latest_charge")
    if not charges:
        return {"status": "ignored"}

    booking.charge_id = charges
    booking.state = BookingState.PENDING
    booking.payment_state = BookingPaymentState.PAID
    booking.paid_amount = payment_intent["amount_received"]
    booking.paid_currency = payment_intent["currency"]

    await db.commit()
    return {"status": "ok"}


async def handle_payment_intent_failed(db, ev):
    payment_intent = ev["data"]["object"]
    payment_intent_id = payment_intent["id"]

    booking = await _find_booking_by_payment_intent(db, payment_intent_id)
        
    if not booking:
        return {"status": "ignored"}

    if booking.state != BookingState.PENDING_PAYMENT:
        return {"status": "already_processed"}
    
    if booking.payment_state == BookingPaymentState.CREATED:
        return {"status": "ignored"}

    if booking.payment_state != BookingPaymentState.IN_PROGRESS:
        return {"status": "already_processed"}

    booking.state = BookingState.CANCELED
    booking.payment_state = BookingPaymentState.FAILED

    await db.commit()
    return {"status": "ok"}


async def handle_charge_refunded(db, ev):
    charge = ev["data"]["object"]

    booking = await _find_booking_by_charge_id(db, charge["id"])

    if not booking:
        return {"status": "ignored"}

    booking.payment_state = BookingPaymentState.REFUNDED
    booking.state = BookingState.CANCELED

    await db.commit()
    return {"status": "ok"}


async def handle_checkout_session_expired(db, ev):
    session = ev["data"]["object"]
    booking_id = session["metadata"].get("booking_id")

    if not booking_id:
        return {"status": "ignored"}

    booking = await _find_booking_by_id(db, booking_id)

    if not booking:
        return {"status": "ignored"}

    if booking.state != BookingState.PENDING_PAYMENT:
        return {"status": "already_processed"}

    booking.state = BookingState.CANCELED
    booking.payment_state = BookingPaymentState.EXPIRED

    await db.commit()
    return {"status": "ok"}


async def handle_payment_intent_canceled(db, ev):
    payment_intent = ev["data"]["object"]
    payment_intent_id = payment_intent["id"]

    booking = await _find_booking_by_payment_intent(db, payment_intent_id)

    if not booking:
        return {"status": "ignored"}

    if booking.payment_state in {
        BookingPaymentState.PAID,
        BookingPaymentState.REFUNDED,
    }:
        return {"status": "already_processed"}

    booking.state = BookingState.CANCELED
    booking.payment_state = BookingPaymentState.CANCELED

    await db.commit()
    return {"status": "ok"}


async def handle_charge_dispute_created(db, ev):
    dispute = ev["data"]["object"]
    charge_id = dispute["charge"]

    booking = await _find_booking_by_charge_id(db, charge_id)

    if not booking:
        return {"status": "ignored"}

    booking.payment_state = BookingPaymentState.DISPUTED
    booking.state = BookingState.ON_HOLD

    await db.commit()
    return {"status": "ok"}


async def handle_account_updated(db, ev):
    account = ev["data"]["object"]

    print(f"stripe_account_id = {account["id"]}")
    worker = await _find_worker_by_stripe_account_id(db, account["id"])
    if not worker:
        return {"status": "ignored"}
    
    print(f"charges_enabled = {account["charges_enabled"]}")

    worker.charges_enabled = account["charges_enabled"]
    worker.payouts_enabled = account["payouts_enabled"]

    await db.commit()
    return {"status": "ok"}


async def handle_account_application_deauthorized(db, ev):
    account = ev["account"]  # NOTE: different shape!

    worker = await _find_worker_by_stripe_account_id(db, account)
    if not worker:
        return {"status": "ignored"}

    worker.stripe_account_id = None
    worker.charges_enabled = False
    worker.payouts_enabled = False
    worker.is_active = False

    await db.commit()
    return {"status": "ok"}


@router.post("/onboarding")
async def stripe_onboarding(
    db: DBSessionDep,
    user_id: CurrentUserIdPanicDep
):
    worker = await get_worker_panic(db, user_id)
    
    if not worker.stripe_account_id:
        account = stripe.Account.create(
            type="express",
            email=worker.user.email
        )
        worker.stripe_account_id = account.id
        db.add(worker)
        await db.commit()
        await db.refresh(worker)

    account_link = stripe.AccountLink.create(
        account=worker.stripe_account_id,
        refresh_url=STRIPE_REFRESH_URL,
        return_url=STRIPE_RETURN_URL,
        type="account_onboarding",
    )

    return {
        "url": account_link.url
    }
