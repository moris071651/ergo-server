from uuid import uuid4
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from app.config.redis import get_redis
from app.config.settings import REDIS_LOGOUT_SET, AUTH_COOKIE_MAX_AGE
from app.config.settings import JWT_ALGORITHM, JWT_SECRET_KEY


def create_access_token(data: dict, expires_delta: Optional[int] = AUTH_COOKIE_MAX_AGE):
    expires_delta = timedelta(seconds=expires_delta)

    to_encode = data.copy()
    to_encode.update({
        "jti": str(uuid4()),
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + expires_delta).timestamp()),
    })

    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm = JWT_ALGORITHM)


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
