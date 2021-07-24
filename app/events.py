import aioredis
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.redis import redis
from app.db.postgres import postgres


async def create_pg_connection():
    postgres.async_pg_engine = create_async_engine(settings.pg_dsn, echo=True)


async def create_redis_connection():
    redis.redis_client = await aioredis.create_redis_pool(settings.REDIS_DSN, minsize=5, maxsize=10)


async def close_pg_connection():
    await postgres.async_pg_engine.dispose()


async def close_redis_connection():
    await redis.redis_client.wait_closed()


on_startup = [create_pg_connection, create_redis_connection]
on_shutdown = [close_pg_connection, close_redis_connection]
