from fastapi import APIRouter
from app.routers.v1.users.me import router as me
from app.routers.v1.users.users import router as users

router = APIRouter(prefix='/v1')

router.include_router(me)
router.include_router(users)