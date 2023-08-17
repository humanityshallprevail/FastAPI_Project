from typing import Any

from redis import asyncio as aioredis  # type: ignore[import]

from config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

if REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'


async def get_redis_connection() -> Any:
    return await aioredis.from_url(REDIS_URL)


async def get_from_cache(key) -> bytes | None:
    connection = await get_redis_connection()
    value = await connection.get(key)
    await connection.close()
    return value


async def set_in_cache(key, value, expiration_time=3600) -> None:
    connection = await get_redis_connection()
    await connection.setex(key, expiration_time, value)
    await connection.close()


async def invalidate_cache(key) -> None:
    connection = await get_redis_connection()
    await connection.delete(key)
    await connection.close()
