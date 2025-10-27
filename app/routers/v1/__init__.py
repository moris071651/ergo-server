from fastapi import APIRouter
from app.routers.v1.auth import router as auth
from app.routers.v1.users import router as users

router = APIRouter(prefix='/v1')

router.include_router(auth)
router.include_router(users)
