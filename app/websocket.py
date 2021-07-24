import asyncio
import logging
from functools import lru_cache

import uvicorn
import uvloop
from aioredis import Redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.authentication import AuthenticationMiddleware

from app.core.config import settings
from app.core.fastapi.auth.decorators import ws_room_permission
from app.core.fastapi.auth.middleware import CustomAuthBackend
from app.core.logger import LOGGING
from app.db.postgres.postgres import get_pg_engine
from app.db.redis.redis import get_redis_client
from app.events import on_startup, on_shutdown
from app.services.ws import WebsocketService

logger = logging.getLogger(__name__)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)

# Activate auth middleware
app.add_middleware(AuthenticationMiddleware, backend=CustomAuthBackend())


@lru_cache()
def get_ws_service(
        db_connection: AsyncEngine = Depends(get_pg_engine),
        redis: Redis = Depends(get_redis_client),
) -> WebsocketService:
    return WebsocketService(db_connection, redis)


async def read_from_stream(room_id: str, service: WebsocketService, websocket: WebSocket):
    while True:
        await service.read_from_stream(room_id=room_id, websocket=websocket)


async def send_to_stream(room_id: str, websocket: WebSocket, service: WebsocketService):
    while True:
        message: str = await websocket.receive_text()
        await service.stream_message(room_id=room_id, message=message, websocket=websocket)


@app.websocket("/ws/{room_id}")
@ws_room_permission()
async def websocket_endpoint(
        websocket: WebSocket,
        room_id: str,
        service: WebsocketService = Depends(get_ws_service),
):
    await service.connect(websocket)
    read = asyncio.create_task(read_from_stream(service=service, websocket=websocket, room_id=room_id))
    write = asyncio.create_task(send_to_stream(service=service, websocket=websocket, room_id=room_id))

    try:
        await asyncio.gather(read, write)
    except WebSocketDisconnect:
        await service.disconnect(room_id=room_id, websocket=websocket)


if __name__ == "__main__":
    uvicorn.run(
        "app.websocket:app",
        host=settings.PROJECT_HOST,
        port=settings.WS_PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
