from fastapi import FastAPI
from app.middlewares.token import TokenMiddleware
from app.routers import router as routers
from app.exceptions import setup_error_handling

app = FastAPI()
app.include_router(routers)

app.add_middleware(TokenMiddleware)

setup_error_handling(app)
