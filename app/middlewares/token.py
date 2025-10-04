from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class TokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, req: Request, call_next):
        token = req.cookies.get('ErgoAuthToken')

        if token == "secret123":
            req.state.user = {"id": 1, "name": "Alice"}

        else:
            req.state.user = None

        return await call_next(req)
