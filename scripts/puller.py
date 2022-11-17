"""
Night's Watch for worker
"""

import os

from minio import Minio
from pprint import pprint
from minio.error import InvalidResponseError

prefix = os.getenv('PREFIX')
pod_name = os.getenv('POD_NAME')
files_service_hosts = os.getenv('FILES_SERVICE_HOSTS')
minio_host =  os.getenv('MINIO_HOST')

minioClient = Minio(
    'dev-minio.atop:9000',
    access_key='admin',
    secret_key='changeme',
    secure=False
)


def get_all_abs_path(source_dir):
    path_list = []
    for fpathe, dirs, fs in os.walk(source_dir):
        for f in fs:
            p = os.path.join(fpathe, f)
            path_list.append(p)
    return path_list


def pull(bucket_name: str, prefix: str):
    try:
        objects = minioClient.list_objects(
            bucket_name,
            prefix=prefix,
            recursive=True
        )
        for obj in objects:
            minioClient.fget_object(
                bucket_name, obj.object_name, f'{obj.object_name}')
            pprint(obj.object_name)
    except InvalidResponseError as err:
        pprint(err)


def push(bucket_name,prefix):
    try:
        if os.path.isdir(prefix):
            object_list = get_all_abs_path(prefix)
        else:
            object_list = [prefix]
        for key in object_list:
            minioClient.fput_object(bucket_name, key, key)
            pprint(f'push: {key}')
        pprint(f'push done')
    except Exception as err:
        pprint(err)


if __name__ == "__main__":
    if prefix == '':
        pass
    else:
        pull('cases', prefix)
