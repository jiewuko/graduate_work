from typing import Optional

from aioredis import Redis


redis_client: Optional[Redis] = None


async def get_redis_client() -> Optional[redis_client]:
    return redis_client
