from fastapi import APIRouter
from app.routers.v1.auth import router as auth

router = APIRouter(prefix='/v1')
router.include_router(auth)
