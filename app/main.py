import os
import logging
from fastapi import FastAPI
from app.config.lifespan import lifespan
from app.config.logging import get_logging_config
from app.middlewares.token import TokenMiddleware
from app.middlewares.user_verify import UserVerifyMiddleware
from app.routers import router as routers
from app.exceptions import setup_error_handling

os.makedirs("logs", exist_ok=True)
logging.config.dictConfig(get_logging_config())
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)
setup_error_handling(app)

# do not switch the places of the middlewares
app.add_middleware(UserVerifyMiddleware)
app.add_middleware(TokenMiddleware)

app.include_router(routers)
