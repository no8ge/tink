import json
import yaml
import traceback
from loguru import logger

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from kubernetes import client
from kubernetes import config
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException

from src.helm import Repo
from src.helm import Chart
from src.error import HelmError
from src.model import PodModel
from src.model import RepoModel
from src.model import ChartModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    config.load_incluster_config()
    api_instance = client.CoreV1Api()
except ConfigException as e:
    if e.args[0] == 'Service host/port is not set.':
        logger.warning(e)
        config.load_kube_config()
        api_instance = client.CoreV1Api()
except Exception as e:
    logger.error(traceback.format_exc())


@app.on_event("startup")
async def startup_event():
    try:
        pass
    except Exception as e:
        logger.debug(e)


@app.get("/v1.0/version")
async def version():
    try:
        with open('chart/Chart.yaml') as f:
            chart = yaml.safe_load(f)
            del chart['apiVersion']
            chart_json = json.dumps(chart)
            logger.info(chart_json)
        return chart_json
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/metrics")
async def metrics(repo: RepoModel):
    logger.info(repo)
    try:
        result = Repo(repo).add()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.post("/v1.0/repo")
async def add_repo(repo: RepoModel):
    logger.info(repo)
    try:
        result = Repo(repo).add()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/repo")
async def list_repo(repo: RepoModel):
    logger.info(repo)
    try:
        result = Repo(repo).list()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.delete("/v1.0/repo")
async def remove_repo(repo: RepoModel):
    logger.info(repo)
    try:
        result = Repo(repo).remove()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.patch("/v1.0/repo")
async def update_repo(repo: RepoModel):
    logger.info(repo)
    try:
        result = Repo(repo).update()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.post("/v1.0/chart")
async def install_chart(ct: ChartModel):
    logger.info(ct)
    try:
        result = Chart(ct).install()
        del result['outs']['manifest']
        del result['outs']['chart']
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.patch("/v1.0/chart")
async def upgrade_chart(ct: ChartModel):
    logger.info(ct)
    try:
        result = Chart(ct).upgrade()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.delete("/v1.0/chart")
async def uninstall_chart(ct: ChartModel):
    logger.info(ct)
    try:
        result = Chart(ct).uninstall()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/chart")
async def get_chart(ct: ChartModel):
    logger.info(ct)
    try:
        result = Chart(ct).list()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/charts")
async def get_chart(ct: ChartModel):
    logger.info(ct)
    try:
        result = Chart(ct).search()
        return result
    except HelmError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/v1.0/proxy/pod")
async def get_pod(pod: PodModel):
    logger.info(pod)
    try:
        result = api_instance.read_namespaced_pod(
            name=pod.name,
            namespace=pod.namespace
        ).to_dict()
        del result['metadata']
        del result['spec']
        logger.info(result)
        return result
    except ApiException as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.delete("/v1.0/proxy/pod")
async def delete_pod(pod: PodModel):
    logger.info(pod)
    try:
        result = api_instance.delete_namespaced_pod(
            name=pod.name,
            namespace=pod.namespace
        ).to_dict()
        del result['metadata']
        del result['spec']
        logger.info(result)
        return result
    except ApiException as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.post("/v1.0/proxy/pod")
async def exec_pod(pod: PodModel):
    logger.info(pod)
    try:
        exec_command = [
            '/bin/sh',
            '-c',
            pod.cmd
        ]
        resp = stream(
            api_instance.connect_get_namespaced_pod_exec,
            pod.name,
            pod.namespace,
            command=exec_command,
            container=pod.container,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False
        )
        logger.info(resp)
        return resp
    except ApiException as e:
        logger.error(traceback.format_exc())
        if e.status == 0:
            raise HTTPException(status_code=500, detail=e.reason)
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')
