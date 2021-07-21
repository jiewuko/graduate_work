from typing import List

from app.models.base import BaseModel


class ResponseModel(BaseModel):
    success: bool
    errors: List[str] = []
