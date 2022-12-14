from typing import Any, Union
from pydantic import BaseModel


class Container(BaseModel):
    image: str
    command: str


class Task(BaseModel):
    type: str
    name: str
    container: Container
    prefix: Union[str, None] = None
