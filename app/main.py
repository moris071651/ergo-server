from fastapi import FastAPI
from app.routers import router as routers
from app.exceptions import setup_error_handling

app = FastAPI()
app.include_router(routers)

setup_error_handling(app)
