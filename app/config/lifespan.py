from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

import stripe

from app.config.redis import close_redis, init_redis
from app.config.settings import BUCKET_LISTING_IMAGES, BUCKET_USER_PICTURE, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.db.session import init_models
from app.utils.storage import get_storage_adapter

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    await init_models()

    if not STRIPE_SECRET_KEY and not STRIPE_WEBHOOK_SECRET:
        raise Exception()

    stripe.api_key = STRIPE_SECRET_KEY

    if not get_storage_adapter().create_bucket(BUCKET_USER_PICTURE):
        logger.info(f"Creation of '{BUCKET_USER_PICTURE}' bucket skipped, already exists")

    if not get_storage_adapter().create_bucket(BUCKET_LISTING_IMAGES):
        logger.info(f"Creation of '{BUCKET_LISTING_IMAGES}' bucket skipped, already exists")

    logger.info("FastAPI started")
    yield
    
    await close_redis()
    logger.info("FastAPI stopped")
