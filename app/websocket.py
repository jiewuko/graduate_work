import logging

import uvicorn
from fastapi import status, FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from starlette.middleware.authentication import AuthenticationMiddleware

from app.core.config import settings
from app.core.fastapi.auth.middleware import CustomAuthBackend
from app.core.fastapi.auth.models import CustomUser
from app.core.logger import LOGGING
from app.events import on_startup, on_shutdown
from app.services.base import WebsocketService

logger = logging.getLogger(__name__)
app = FastAPI(
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)
ws_service = WebsocketService()

# Activate auth middleware
app.add_middleware(AuthenticationMiddleware, backend=CustomAuthBackend())

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8001/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


async def get_user(
        websocket: WebSocket,
):
    if not websocket.user.is_authenticated:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return websocket.user


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        client_id: int,
        user: CustomUser = Depends(get_user),
):
    await ws_service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_service.broadcast(f"{user.display_name}: {data}")
    except WebSocketDisconnect:
        ws_service.disconnect(websocket)
        await ws_service.broadcast(f"{user.display_name} left the chat")


if __name__ == "__main__":
    uvicorn.run(
        "app.websocket:app",
        host=settings.PROJECT_HOST,
        port=settings.PROJECT_PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
    )
