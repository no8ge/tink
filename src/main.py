import traceback
from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from src.utils.locust import Locust
from src.utils.aomaker import Aomaker
from src.utils.base_job import BaseJob
from src.utils.pod import Pod
from src.model import Task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

p = Pod()


@app.post("/tink/pod")
async def create_pod(task: Task):
    logger.info(task)
    try:
        result = p.create_pod(task).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.get("/tink/pod/{name}")
async def get_pod(name):
    try:
        result = p.get_pod(name).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.delete("/tink/pod/{name}")
async def delete_pod(name):
    try:
        result = p.delete_pod(name).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.post("/tink/job")
async def create_job(task: Task):
    logger.info(task)
    try:
        if task.type == 'aomaker':
            result = Aomaker().create_job(task).to_dict()
        elif task.type == 'locust':
            result = Locust().create_job(task).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.get("/tink/job/{name}")
async def get_job(name):
    try:
        result = BaseJob().get_job(name).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.delete("/tink/job/{name}")
async def delete_job(name):
    try:
        result = BaseJob().delete_job(name).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)
