from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.token import decode_access_token
from app.config.settings import AUTH_COOKIE_KEY

class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, req: Request, call_next):
        token = req.cookies.get(AUTH_COOKIE_KEY)
        req.state.user_id = None

        if token:
            payload = decode_access_token(token)
            if payload and (user_id := payload.get("user_id")):
                req.state.user_id = user_id

        response = await call_next(req)
        return response
