import traceback
from loguru import logger
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from src.model import Task
from src.utils.pod import Pod
from src.helper import EsHelper
from src.env import ELASTICSEARCH_SERVICE_HOSTS


index = 'tink'
app = FastAPI()
es = EsHelper(ELASTICSEARCH_SERVICE_HOSTS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        es.index(index)
    except Exception as e:
        logger.debug(e)


@app.post("/tink/job")
async def create_job(task: Task):
    logger.info(task)
    try:
        result = Pod().create_job(task).to_dict()
        data = task.dict()
        data['timestamp'] = datetime.now()
        es.insert(
            index,
            task.name,
            data
        )
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.get("/tink/job/{name}")
async def get_job(name):
    try:
        result = Pod().get_job(name).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.delete("/tink/job/{name}")
async def delete_job(name):
    try:
        result = Pod().delete_job(name).to_dict()
        es.delete(index,name)
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.get("/tink/jobs")
async def get_job(_from: int, size: int):
    result = es.search(index, {}, _from, size, mod='match_all')
    resp = {}
    total = result['hits']['total']['value']
    hits = result['hits']['hits']
    _sources = list(map(lambda x: x['_source'], hits))
    resp['total'] = total
    resp['_sources'] = _sources
    return resp
