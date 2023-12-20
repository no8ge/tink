import re
import uuid
from typing import Optional, Union, Dict
from pydantic import AnyHttpUrl, BaseModel, constr, validator
from dataclasses import dataclass


class RepoModel(BaseModel):
    name: constr(min_length=2, max_length=16)
    url: AnyHttpUrl
    label: Optional[Dict[str, str]] = None


class ChartModel(BaseModel):
    release: str
    chart: str
    repo: str
    namespace: str = 'default'
    version: str = None
    value: Optional[Dict[str, str]] = None

    @validator('repo')
    def name_must_be_str(cls, v):
        assert isinstance(v, str), 'must be a string'
        return v

    @validator('release')
    def validate_release_uuid(cls, value):
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            raise ValueError("release must be uuid string")


class PodModel(BaseModel):
    name: str
    cmd: Union[str, None] = None
    container: Union[str, None] = None
    namespace: str = None
