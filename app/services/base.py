from typing import List

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.websockets import WebSocket

__all__ = (
    'BaseService',
    'WebsocketService'
)


class BaseService:
    def __init__(self, db_connection: AsyncEngine):
        self.db_connection = db_connection

    def get_session(self) -> AsyncSession:
        return sessionmaker(self.db_connection, expire_on_commit=False, class_=AsyncSession)()


class WebsocketService:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
