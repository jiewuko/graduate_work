from pydantic.validators import UUID

from app.models.base import BaseModel


class UserModel(BaseModel):
    id: UUID
    first_name: str
    last_name: str
