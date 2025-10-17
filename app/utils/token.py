from uuid import uuid4
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from app.config.redis import redis_client


SECRET_KEY = "super-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    to_encode.update({
        "jti": str(uuid4()),
        "exp": datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
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
        await redis_client.sadd("revoked_tokens", jti)
        await redis_client.expire("revoked_tokens", ttl)


async def is_token_revoked(jti: str) -> bool:
    return await redis_client.sismember("revoked_tokens", jti)
