import os
from minio import Minio
from pprint import pprint


report = os.getenv('REPORT')
prefix = os.getenv('PREFIX')
minio_host = os.getenv('MINIO_HOST')


minioClient = Minio(
    minio_host,
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


def push(bucket_name, prefix):
    try:
        if os.path.isdir(report):
            object_list = get_all_abs_path(report)
        else:
            object_list = [report]
        for key in object_list:
            minioClient.fput_object(bucket_name, f'{prefix}{key}', key)
        pprint('push done')
    except Exception as err:
        pprint(err)


if __name__ == "__main__":
    if prefix == '':
        pass
    else:
        if os.path.exists(report):
            try:
                push('result', prefix)
                os.system(f"mkdir -p /report/{prefix}{report}")
                os.system(f"/bin/cp -rf {report}/* /report/{prefix}{report}")
            except Exception as err:
                pprint(err)
        else:
            pprint('report not exists')
