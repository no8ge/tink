from typing import Any, Union
from pydantic import BaseModel


class VolumeMount(BaseModel):
    log_mount_path: str
    report_mount_path: Union[str, None] = None
    ext_mount_path: Union[Any, None] = None


class Container(BaseModel):
    image: str
    command: str
    volume_mounts: Union[VolumeMount, None] = None


class Task(BaseModel):
    type: str
    name: str
    container: Container
    log_name: str
    project_id: Union[str, None] = None
    report_id: Union[str, None] = None
