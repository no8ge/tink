import re
import uuid
from typing import  Optional, Union
from pydantic import BaseModel, validator
from dataclasses import dataclass


class RepoModel(BaseModel):
    name: str
    url: str
    label: Union[str, None] = None

    @validator('name')
    def name_must_be_str(cls, v):
        assert isinstance(v, str), 'must be a string'
        return v


class ChartModel(BaseModel):
    release: str
    chart: str
    repo: str
    namespace: str = None
    version: str = None
    value: dict = None


class PodModel(BaseModel):
    name: str
    cmd: Union[str, None] = None
    container: Union[str, None] = None
    namespace: str
