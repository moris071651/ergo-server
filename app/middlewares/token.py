from fastapi import Request
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.db.session import get_db
from app.models.users import User

from app.utils.token import decode_access_token, is_token_valid
from app.config.settings import AUTH_COOKIE_KEY

class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, req: Request, call_next):
        token = req.cookies.get(AUTH_COOKIE_KEY)
        req.state.user = None
        
        payload = decode_access_token(token) if token else None
        user_id = payload.get("user_id") if payload else None
        req.state.jwt = payload

        if payload and not await is_token_valid(payload['jti'], payload['exp']):
            user_id = None

        if user_id:
            async for db in get_db():
                result = await db.execute(select(User).filter(User.id == user_id))
                user = result.scalars().first()

                if user:
                    req.state.user = user

                break

        response = await call_next(req)
        return response
