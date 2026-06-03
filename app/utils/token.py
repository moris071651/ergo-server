import hashlib
from uuid import uuid4
from fastapi import HTTPException
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from app.config.redis import get_redis
from app.config.settings import ACCESS_TOKEN_EXPIRE, AUTH_ACCESS_COOKIE_KEY, AUTH_REFRESH_COOKIE_KEY, REDIS_LOGOUT_SET, REFRESH_TOKEN_EXPIRE
from app.config.settings import JWT_ALGORITHM, JWT_SECRET_KEY


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(data: Dict[str, Any]) -> str:
    now = datetime.utcnow()
    payload = {
        "dat": data,
        "type": "access",
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ACCESS_TOKEN_EXPIRE)).timestamp()),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(sid: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sid": sid,
        "type": "refresh",
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=REFRESH_TOKEN_EXPIRE)).timestamp()),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str, expected_type: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return payload
    
    except JWTError | ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def create_session(user_id: str) -> Tuple[str, str]:
    sid = str(uuid4())
    refresh_token = create_refresh_token(sid)
    refresh_hash = hash_token(refresh_token)

    redis = get_redis()
    await redis.hset(
        f"session:{sid}",
        mapping = {
            "refresh_hash": refresh_hash,
            "user_id": user_id,
        }
    )

    await redis.expire(f"session:{sid}", REFRESH_TOKEN_EXPIRE)

    return refresh_token, sid


REDIS_ACCESS_SET = "active_access_tokens"
async def refresh_session(refresh_token: str, access_token: Optional[str]) -> Tuple[str, str]:
    payload = decode_token(refresh_token, "refresh")
    sid = payload["sid"]

    redis = get_redis()
    session_key = f"session:{sid}"

    session = await redis.hgetall(session_key)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    if access_token:
        incoming_access_hash = hash_token(access_token)
        await redis.srem(REDIS_ACCESS_SET, incoming_access_hash)

    incoming_refresh_hash = hash_token(refresh_token)
    stored_refresh_hash = await redis.hget(session_key, "refresh_hash")

    if incoming_refresh_hash != stored_refresh_hash:
        await redis.delete(session_key)
        raise HTTPException(status_code=401, detail="Refresh token reused")
    
    now = datetime.utcnow()
    if int(now.timestamp()) >= payload["exp"]:
        await redis.delete(session_key)
        raise HTTPException(status_code=401, detail="Refresh token expired")

    new_refresh = create_refresh_token(sid)
    new_refresh_hash = hash_token(new_refresh)
    await redis.hset(session_key, "refresh_hash", new_refresh_hash)
    await redis.expire(session_key, REFRESH_TOKEN_EXPIRE)

    user_id = await redis.hget(session_key, "user_id")

    new_access = create_access_token({"id": user_id})
    new_access_hash = hash_token(new_access)

    await redis.sadd(REDIS_ACCESS_SET, new_access_hash)
    await redis.expire(REDIS_ACCESS_SET, ACCESS_TOKEN_EXPIRE)

    return new_access, new_refresh


async def verify_refresh_token(refresh_token: Optional[str]) -> bool:
    if not refresh_token:
        return False
    
    payload = decode_token(refresh_token, "refresh")
    sid = payload["sid"]

    redis = get_redis()
    session_key = f"session:{sid}"
    
    incoming_refresh_hash = hash_token(refresh_token)
    stored_refresh_hash = await redis.hget(session_key, "refresh_hash")

    if incoming_refresh_hash != stored_refresh_hash:
        await redis.delete(session_key)
        return False

    now = datetime.utcnow()
    if int(now.timestamp()) >= payload["exp"]:
        await redis.delete(session_key)
        return False
    
    return True


async def invalidate_session(refresh_token: str, access_token: str):
    payload = decode_token(refresh_token, "refresh")
    sid = payload["sid"]

    redis = get_redis()
    session_key = f"session:{sid}"

    incoming_access_hash = hash_token(access_token)
    await redis.srem(REDIS_ACCESS_SET, incoming_access_hash)
    await redis.delete(session_key)


async def is_access_token_active(access_token: Optional[str]) -> bool:
    if not access_token:
        return False
    
    access_hash = hash_token(access_token)

    redis = get_redis()
    return await redis.sismember(REDIS_ACCESS_SET, access_hash) == 1


async def is_access_token_valid(access_token: str) -> bool:
    payload = decode_token(access_token, "access")

    now = datetime.utcnow()
    if payload["exp"] <= now:
        return False

    return await is_access_token_active(access_token)


async def get_access_token_data(access_token: str) -> Dict[str, Any]:
    payload = decode_token(access_token, "access")

    now = int(datetime.utcnow().timestamp())
    if payload["exp"] <= now:
        raise HTTPException(status_code=401, detail="Access token expired")

    active = await is_access_token_active(access_token)
    if not active:
        raise HTTPException(status_code=401, detail="Access token revoked")

    return payload["dat"]


async def get_access_token_payload(access_token: str) -> Dict[str, Any]:
    payload = decode_token(access_token, "access")

    now = int(datetime.utcnow().timestamp())
    if payload["exp"] <= now:
        raise HTTPException(status_code=401, detail="Access token expired")

    active = await is_access_token_active(access_token)
    if not active:
        raise HTTPException(status_code=401, detail="Access token revoked")

    return payload


async def mark_access_token_active(access_token: str):
    access_hash = hash_token(access_token)

    redis = get_redis()
    await redis.sadd(REDIS_ACCESS_SET, access_hash)
    await redis.expire(REDIS_ACCESS_SET, ACCESS_TOKEN_EXPIRE)
