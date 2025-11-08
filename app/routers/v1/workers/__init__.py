from fastapi import APIRouter
from app.routers.v1.workers.me import router as me

router = APIRouter(prefix='/workers')

router.include_router(me)