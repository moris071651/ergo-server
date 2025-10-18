from uuid import uuid4
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from app.config.redis import redis_client
from app.config.settings import REDIS_LOGOUT_SET


SECRET_KEY = "super-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    to_encode.update({
        "jti": str(uuid4()),
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + expires_delta).timestamp()),
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    
    except JWTError:
        return None
    

async def revoke_token(jti: str, exp_timestamp: int):
    ttl = exp_timestamp - int(datetime.utcnow().timestamp())
    if ttl > 0:
        await redis_client.sadd(REDIS_LOGOUT_SET, jti)
        await redis_client.expire(REDIS_LOGOUT_SET, ttl)


async def is_token_revoked(jti: str) -> bool:
    return await redis_client.sismember(REDIS_LOGOUT_SET, jti)


async def is_token_valid(jti: str, exp: int) -> bool:
    revoked = await is_token_revoked(jti)
    not_expired = exp > int(datetime.utcnow().timestamp())
    return (not revoked) and not_expired
