from fastapi import APIRouter
from app.routers.v1 import router as v1

router = APIRouter(prefix='/api')
router.include_router(v1)
