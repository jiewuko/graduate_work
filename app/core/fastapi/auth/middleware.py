import logging

import jwt
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    UnauthenticatedUser,
)

from app.core.config import settings
from app.core.fastapi.auth.models import CustomUser

logger = logging.getLogger(__name__)
security = HTTPBearer()


class CustomAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        # Get JWT token from auth header
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            return AuthCredentials(), UnauthenticatedUser()

        if not credentials:
            return AuthCredentials(), UnauthenticatedUser()

        # Checks the validity of the JWT token, if token is invalid returns UnauthenticatedUser object
        try:
            jwt_decoded = jwt.decode(credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALG])
        except jwt.DecodeError:
            return AuthCredentials(), UnauthenticatedUser()

        # In case if token is valid returns an object of the authorized user
        try:
            auth_user = CustomUser(
                pk=jwt_decoded['sub'],
                first_name=jwt_decoded['first_name'],
                last_name=jwt_decoded['last_name'],
            )
        except KeyError:
            logger.error(f'Bad signature for user: {jwt_decoded}')
            return AuthCredentials(), UnauthenticatedUser()

        return AuthCredentials(["authenticated"]), auth_user
