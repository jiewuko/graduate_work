import aioredis
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db import redis
from app.db.postgres import postgres
from app.models.db.room import Base


async def create_pg_connection():
    postgres.async_pg_engine = create_async_engine(settings.pg_dsn, echo=True)
    # async with postgres.async_pg_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)


# async def create_redis_connection():
#     redis.redis_client = await aioredis.create_redis_pool(settings.REDIS_DSN)


async def close_pg_connection():
    await postgres.async_pg_engine.dispose()


#
# async def close_redis_connection():
#     await redis.redis_client.close()


on_startup = [create_pg_connection]
on_shutdown = [close_pg_connection]