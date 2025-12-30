from fastapi import APIRouter
from app.routers.v1.auth import router as auth
from app.routers.v1.users import router as users
from app.routers.v1.workers import router as workers
from app.routers.v1.listings import router as listings

router = APIRouter(prefix='/v1')

router.include_router(auth)
router.include_router(users)
router.include_router(workers)
router.include_router(listings)
