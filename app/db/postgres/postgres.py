from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine


async_pg_engine: Optional[AsyncEngine] = None


async def get_pg_engine() -> Optional[async_pg_engine]:
    return async_pg_engine
