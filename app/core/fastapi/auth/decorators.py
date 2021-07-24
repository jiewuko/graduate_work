import functools

from fastapi import HTTPException, status
from pydantic.validators import UUID
from starlette.requests import Request

from app.services.ws import WebsocketService

__all__ = ('login_required', 'ws_room_permission')


def is_auth_user(request: Request) -> bool:
    try:
        user = getattr(request, 'user')
        is_auth = getattr(user, 'is_authenticated')
        return is_auth

    except AttributeError:
        return False


def login_required():
    def wrapper(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            request = kwargs.get('request')
            if not request or not is_auth_user(request):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login required!')

            return await func(*args, **kwargs)

        return inner

    return wrapper


def ws_room_permission():
    def wrapper(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            websocket = kwargs.get('websocket')
            if not websocket or not websocket.user.is_authenticated:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            service: WebsocketService = kwargs.get('service')
            room_id: UUID = kwargs.get('room_id')
            room = await service.get_room(room_id=room_id, user=websocket.user)
            if not room:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            return await func(*args, **kwargs)

        return inner

    return wrapper
