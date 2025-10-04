from fastapi import FastAPI
from app.routers import router as routers

app = FastAPI()
app.include_router(routers)
