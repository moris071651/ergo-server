from app.config.redis import get_redis


async def acquire_event_lock(
    event_id: str,
    ttl_seconds: int = 60 * 60 * 24 * 7,
) -> bool:
    key = f"stripe:event:{event_id}"
    return await get_redis().set(key, "1", ex=ttl_seconds, nx=True) is True
