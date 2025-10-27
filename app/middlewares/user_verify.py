from uuid import UUID
from fastapi import Request
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import get_db
from app.utils.user import user_exists


class UserVerifyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, req: Request, call_next):
        req.state.user_id = None

        payload = getattr(req.state, "jwt", None)
        user_id = payload.get("id") if payload else None

        if user_id:
            async for db in get_db():
                if await user_exists(db, user_id):
                    req.state.user_id = UUID(user_id)
                break

        response = await call_next(req)
        return response
