import os
import shutil
from minio import Minio
from loguru import logger


logger.info('====== atop 开始处理测试报告 ======')
report = os.getenv('REPORT')
logger.info(f'测试报告路径为: {report}')

prefix = os.getenv('PREFIX')
logger.info(f'测试报告名称为: {prefix}')

minio_host = os.getenv('MINIO_HOST')


def get_all_abs_path(source_dir):
    path_list = []
    for fpathe, dirs, fs in os.walk(source_dir):
        for f in fs:
            p = os.path.join(fpathe, f)
            path_list.append(p)
    return path_list


def push(bucket_name, prefix):

    try:
        minioClient = Minio(
            minio_host,
            access_key='admin',
            secret_key='changeme',
            secure=False
        )
        logger.info('minio客户端连接成功')
    except Exception as err:
        logger.info('minio客户端连接失败')
        logger.debug(err)

    try:
        if os.path.isdir(report):
            object_list = get_all_abs_path(report)
        else:
            object_list = [report]
        logger.info('==开始备份测试报告至minio')
        for key in object_list:
            minioClient.fput_object(bucket_name, prefix+key, key)
            logger.info(f'上传 {key}')
        logger.info('==测试报告已备份至minio')
    except Exception as err:
        logger.info('测试报告备份至minio失败')
        logger.debug(err)


if __name__ == "__main__":
    if os.path.exists(report):
        try:
            source_folder = report
            target_folder = f"/report/{prefix}{report}"
            # target_folder = f"report/{prefix}/{report}" # 本地测试路径

            try:
                shutil.rmtree(target_folder)
                logger.info(f'存在同名目录: {target_folder}')
                logger.info(f'删除同名目录: {target_folder}')
            except FileNotFoundError:
                pass
            
            logger.info(f'开始复制测试报告到文件服务器共享存储目录:{target_folder} ...')
            shutil.copytree(source_folder, target_folder)
            logger.info('复制完成')

            push('result', prefix)
        except Exception as err:
            logger.debug(err)
    else:
        logger.info('测试报告不存在')

    logger.info('======= atop 完成测试报告处理 =======')
