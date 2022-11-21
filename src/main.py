import traceback
from loguru import logger
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from src.task import Task
from src.model import Task as TK
from src.env import ELASTICSEARCH_SERVICE_HOSTS
from src.helper import EsHelper, PrometheusHekper


index = 'tink'
app = FastAPI()
es = EsHelper(ELASTICSEARCH_SERVICE_HOSTS)
ph = PrometheusHekper()

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
async def create_job(task: TK):
    logger.info(task)
    try:
        result = Task(task).create().to_dict()
        data = task.dict()
        data['timestamp'] = datetime.now()
        data['status'] = 'ready'
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
        result = Task().get(name).to_dict()
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.delete("/tink/job/{name}")
async def delete_job(name):
    try:
        result = Task().delete(name).to_dict()
        es.delete(index, name)
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


@app.get('/tink/metrics', response_class=PlainTextResponse)
async def metrics():

    result = es.search('tink', {}, 0, 10000, mod='match_all')
    _sources = list(map(lambda x: x['_source'], result['hits']['hits']))

    for s in _sources:
        resp = Task().get(s['name']).to_dict()
        for _ in resp['status']['container_statuses']:
            if _['name'] != s['name'] and s['status'] != 'Completed':
                if _['state']['running'] != None:
                    s['status'] = 'running'
                if _['state']['waiting'] != None:
                    s['status'] = 'waiting'
                if _['state']['terminated'] != None:
                    s['status'] = _['state']['terminated']['reason']
        es.update(index, s['name'], s)
        ph.tink_task_status.labels(s['name'], s['type'], s['status']).set(1)
    return ph.generate_latest()
