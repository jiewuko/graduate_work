import orjson
from pydantic import BaseModel as PydanticBaseModel

from app.utils import orjson_dumps


class BaseModel(PydanticBaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
