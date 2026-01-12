from uuid import uuid4
from fastapi import HTTPException, Request, Response
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from app.config.redis import get_redis
from app.config.settings import ACCESS_TOKEN_EXPIRE, AUTH_ACCESS_COOKIE_KEY, AUTH_REFRESH_COOKIE_KEY, REDIS_LOGOUT_SET, REFRESH_TOKEN_EXPIRE
from app.config.settings import JWT_ALGORITHM, JWT_SECRET_KEY


def create_access_token(data: dict):
    return _create_token(data, ACCESS_TOKEN_EXPIRE, token_type="access")


def create_refresh_token(data: dict):
    return _create_token(data, REFRESH_TOKEN_EXPIRE, token_type="refresh")


def _create_token(data: dict, expires_seconds: int, token_type: str):
    now = datetime.utcnow()
    payload = {
        **data,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_seconds)).timestamp()),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != expected_type:
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms = [JWT_ALGORITHM])
        return payload
    
    except JWTError:
        return None
    

async def revoke_token(jti: str, exp_timestamp: int):
    ttl = exp_timestamp - int(datetime.utcnow().timestamp())
    if ttl > 0:
        await get_redis().sadd(REDIS_LOGOUT_SET, jti)
        await get_redis().expire(REDIS_LOGOUT_SET, ttl)


async def is_token_revoked(jti: str) -> bool:
    return await get_redis().sismember(REDIS_LOGOUT_SET, jti) == 1


async def is_token_valid(jti: str, exp: int) -> bool:
    revoked = await is_token_revoked(jti)
    not_expired = exp > int(datetime.utcnow().timestamp())
    return (not revoked) and not_expired


async def invalidate_session(req: Request, res: Response):
    for key, token_type in (
        (AUTH_ACCESS_COOKIE_KEY, "access"),
        (AUTH_REFRESH_COOKIE_KEY, "refresh"),
    ):
        token = req.cookies.get(key)
        if not token:
            continue

        payload = decode_token(token, expected_type=token_type)
        await revoke_token(payload["jti"], payload["exp"])

    res.delete_cookie(AUTH_ACCESS_COOKIE_KEY)
    res.delete_cookie(AUTH_REFRESH_COOKIE_KEY)
