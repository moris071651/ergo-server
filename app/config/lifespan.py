from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.config.redis import close_redis, init_redis
from app.config.settings import BUCKET_USER_PICTURE
from app.db.session import init_models
from app.utils.storage import get_storage_adapter

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    await init_models()

    if not get_storage_adapter().create_bucket(BUCKET_USER_PICTURE):
        logger.info(f"Creation of '{BUCKET_USER_PICTURE}' bucket skipped, already exists")

    logger.info("FastAPI started")
    yield
    await close_redis()
    logger.info("FastAPI stopped")
