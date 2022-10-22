FROM python:3.9.12-slim

WORKDIR /cache
RUN apt-get update \
    && apt-get install git -y \
    && pip install minio

CMD ["python","init_containers.py"]