import os
import logging
from fastapi import FastAPI
from app.config.lifespan import lifespan
from app.config.logging import get_logging_config
from app.middlewares.token import TokenMiddleware
from app.routers import router as routers
from app.exceptions import setup_error_handling
from fastapi.middleware.cors import CORSMiddleware


os.makedirs("logs", exist_ok=True)
logging.config.dictConfig(get_logging_config())
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)
setup_error_handling(app)

# do not switch the places of the middlewares
app.add_middleware(TokenMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers)
