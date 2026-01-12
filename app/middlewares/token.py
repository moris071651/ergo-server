from fastapi import Request
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import AUTH_ACCESS_COOKIE_KEY

from app.utils.token import decode_access_token, is_token_valid


class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, req: Request, call_next):
        token = req.cookies.get(AUTH_ACCESS_COOKIE_KEY)
        payload = decode_access_token(token) if token else None

        if payload:
            jti = payload.get("jti")
            exp = payload.get("exp")

            if not await is_token_valid(jti, exp): 
                payload = None

        req.state.jwt = payload
        response = await call_next(req)
        return response
