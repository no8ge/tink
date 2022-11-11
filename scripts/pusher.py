"""
Night's Watch for worker
"""

import os

from minio import Minio
from pprint import pprint
from minio.error import InvalidResponseError

prefix = os.getenv('PREFIX')

minioClient = Minio(
    # 'middleware-minio.tink:9000',
    '127.0.0.1:9000',
    access_key='admin',
    secret_key='changeme',
    secure=False
)


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
            object_list = []
            for _ in os.listdir(prefix):
                object_list.append(os.path.join(prefix, _))
        else:
            object_list = [prefix]
        for key in object_list:
            minioClient.fput_object('atop', key, key)
            pprint(f'push object: {key}')
    except Exception as err:
        pprint(err)


if __name__ == "__main__":
    push(prefix)
