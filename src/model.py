import re
import uuid
from typing import Any, Union
from pydantic import BaseModel, validator


class Container(BaseModel):
    image: str
    command: str


class Task(BaseModel):
    type: str
    name: str
    uid: Union[str, uuid.UUID]
    container: Container
    prefix: Union[str, None] = None

    @validator('name')
    def check_name(cls, name):
        if len(name) > 253:
            raise ValueError('Name must not exceed 253 characters')
        elif not re.match(r'^[a-z0-9][a-z0-9\-\.]*[a-z0-9]$', name):
            raise ValueError(
                'Name must start and end with a lowercase letter or number and contain only lowercase letters, numbers, dash (-), and dot (.)')
        return name

    @validator('type')
    def check_type(cls, type):
        if type not in ["aomaker", "hatbox"]:
            raise ValueError('Type must be aomaker or hatbox')
        return type


class ContainerValue(BaseModel):
    image: str
    command: str
    report: str


class ConfigMapValue(BaseModel):
    testbed: dict
    testcases: dict


class ChartValue(BaseModel):
    type: str
    name: str
    uid: uuid.UUID
    container: ContainerValue
    configmap: Union[ConfigMapValue, None] = None

    @validator('name')
    def check_name(cls, name):
        if len(name) > 253:
            raise ValueError('Name must not exceed 253 characters')
        elif not re.match(r'^[a-z0-9][a-z0-9\-\.]*[a-z0-9]$', name):
            raise ValueError(
                'Name must start and end with a lowercase letter or number and contain only lowercase letters, numbers, dash (-), and dot (.)')
        return name

    @validator('uid')
    def check_uid(cls, uid):
        if not isinstance(uid, uuid.UUID):
            try:
                uid = uuid.UUID(uid)
            except:
                raise ValueError('Invalid UUID')
        return uid

    @validator('type')
    def check_type(cls, type):
        if type not in ["aomaker", "hatbox"]:
            raise ValueError('Type must be aomaker or hatbox')
        return type

    @validator('configmap')
    def check_configmap(cls, configmap):
        if type == "hatbox" and configmap == None:
            raise ValueError('Configmap must not be None')
        return configmap


class PodValue(BaseModel):
    type: str
    name: str
    uid: uuid.UUID
    cmd: Union[str, None] = None
    configmap: Union[ConfigMapValue, None] = None

    @validator('name')
    def check_name(cls, name):
        if len(name) > 253:
            raise ValueError('Name must not exceed 253 characters')
        elif not re.match(r'^[a-z0-9][a-z0-9\-\.]*[a-z0-9]$', name):
            raise ValueError(
                'Name must start and end with a lowercase letter or number and contain only lowercase letters, numbers, dash (-), and dot (.)')
        return name

    @validator('uid')
    def check_uid(cls, uid):
        if not isinstance(uid, uuid.UUID):
            try:
                uid = uuid.UUID(uid)
            except:
                raise ValueError('Invalid UUID')
        return uid

    @validator('type')
    def check_type(cls, type):
        if type not in ["aomaker", "hatbox"]:
            raise ValueError('Type must be aomaker or hatbox')
        return type

    @validator('configmap')
    def check_configmap(cls, configmap):
        if type == "hatbox" and configmap == None:
            raise ValueError('Configmap must not be None')
        return configmap
