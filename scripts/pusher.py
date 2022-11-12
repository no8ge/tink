"""
Night's Watch for worker
"""

import os
import requests

from minio import Minio
from pprint import pprint
from minio.error import InvalidResponseError

prefix = os.getenv('PREFIX')
pod_name = os.getenv('POD_NAME')
files_service_hosts = os.getenv('FILES_SERVICE_HOSTS')


minioClient = Minio(
    '127.0.0.1:9000',
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
            pprint(
                [
                    obj.bucket_name,
                    obj.object_name.encode('utf-8'),
                    obj.last_modified,
                    obj.etag,
                    obj.size,
                    obj.content_type
                ]
            )
            minioClient.fget_object(
                'atop', obj.object_name, f'{obj.object_name}')
    except InvalidResponseError as err:
        pprint(err)


def push(prefix):
    try:
        if os.path.isdir(prefix):
            object_list = get_all_abs_path(prefix)
        else:
            object_list = [prefix]
        for key in object_list:
            minioClient.fput_object('atop', pod_name+key, key)
            pprint(f'push: {key}')
        pprint(f'push done')
    except Exception as err:
        pprint(err)


if __name__ == "__main__":
    if prefix == '':
        pass
    else:
        push(prefix)
        r = requests.get(
            f'http://{files_service_hosts}/files/generate_report/{pod_name}')
        pprint(r.json())
