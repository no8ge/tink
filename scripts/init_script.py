"""
init script for boxter
"""

import os
from minio import Minio
from pprint import pprint


SOURCE = os.getenv('SOURCE')
PROJECT = os.getenv('PROJECT')
TARGET_PATH = '/cache'


if SOURCE == 'gitlab':
    TOKEN = os.getenv('TOKEN')
    URL = os.getenv('URL')
    ORG = os.getenv('ORG')
    os.system(
        f'git clone https://oauth2:{TOKEN}@{URL}/{ORG}/{PROJECT}.git {TARGET_PATH}/{PROJECT}'
    )
    pprint('done')


if SOURCE == 'atop':
    URL = 'middleware-minio.tink:9000'
    USER = 'admin'
    PASSWORD = 'changeme'

    pprint(f'start get testcode from minio@{PROJECT}')
    minioClient = Minio(
        URL,
        access_key=USER,
        secret_key=PASSWORD,
        secure=False
    )

    def obj_to_dict(x):
        return {
            'bucket_name': x.bucket_name,
            'object_name': x.object_name,
            'is_dir': x.is_dir,
            'size': x.size,
            'etag': x.etag,
            'last_modified': x.last_modified,
            'content_type': x.content_type,
            'metadata': x.metadata,
        }

    def get_dirs(bucket_name, prefix=None):
        dirs = minioClient.list_objects(
            bucket_name=bucket_name,
            prefix=prefix,
            recursive=False
        )
        return list(map(obj_to_dict, dirs))

    def get_objs(bucket_name, prefix=None):
        objs = minioClient.list_objects(
            bucket_name=bucket_name,
            prefix=prefix,
            recursive=True
        )
        return list(map(obj_to_dict, objs))

    for i in list(map(lambda x: x['object_name'], get_objs(bucket_name=SOURCE, prefix=PROJECT))):
        file_path = f'{TARGET_PATH}/{i}'
        minioClient.fget_object(
            bucket_name=SOURCE,
            object_name=i,
            file_path=file_path
        )
        pprint(f'download {file_path} from minio@{PROJECT}')
    pprint('done')
