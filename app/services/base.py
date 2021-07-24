from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

__all__ = (
    'BaseService',
)


class BaseService:
    def __init__(self, db_connection: AsyncEngine, redis: Redis):
        self.db_connection = db_connection
        self.redis = redis

    def get_session(self) -> AsyncSession:
        return sessionmaker(self.db_connection, expire_on_commit=False, class_=AsyncSession)()
