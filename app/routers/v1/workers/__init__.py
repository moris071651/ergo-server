from fastapi import APIRouter
from app.routers.v1.workers.me import router as me
from app.routers.v1.workers.worker import router as worker
from app.routers.v1.workers.address import router as address
from app.routers.v1.workers.skills import router as skills1
from app.routers.v1.workers.skills import router_skills as skills2

router = APIRouter(prefix='/workers')

router.include_router(me)
router.include_router(worker)
router.include_router(address)
router.include_router(skills1)
router.include_router(skills2)
