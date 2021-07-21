import functools

from fastapi import HTTPException, status

__all__ = ('login_required',)

from starlette.requests import Request


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
