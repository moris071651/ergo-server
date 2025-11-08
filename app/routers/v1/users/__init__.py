from fastapi import APIRouter
from app.routers.v1.users.me import router as me
from app.routers.v1.users.users import router as users
from app.routers.v1.users.address import router as address

router = APIRouter(prefix='/users')

router.include_router(me)
router.include_router(address)
router.include_router(users)
