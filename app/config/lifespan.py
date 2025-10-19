from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.config.redis import close_redis, init_redis
from app.db.session import init_models

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    await init_models()
    logger.info("FastAPI started")
    yield
    await close_redis()
    logger.info("FastAPI stopped")
