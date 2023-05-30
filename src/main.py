import traceback
from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.task import Task
from src.model import Task as TK
from src.env import NAMESPACE
from src.chart import AsLiteral, yaml
from src.chart import Chart, ChartError
from src.model import PodValue, ChartValue

from kubernetes import client
from kubernetes import config
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException


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


@app.post("/tink/job")
async def create_job(task: TK):
    logger.info(task)
    try:
        result = Task(task).create().to_dict()
        del result['metadata']
        del result['spec']
        logger.info(result)
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.get("/tink/job/{name}")
async def get_job(name):
    try:
        result = Task().get(name).to_dict()
        del result['metadata']
        del result['spec']
        logger.info(result)
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.delete("/tink/job/{name}")
async def delete_job(name):
    try:
        result = Task().delete(name).to_dict()
        del result['metadata']
        del result['spec']
        logger.info(result)
        return result
    except Exception as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)


@app.post("/tink/v1.1/chart")
async def chart_install(value: ChartValue):
    logger.info(value)
    try:
        result = Chart(value).install()
        return result
    except ChartError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.patch("/tink/v1.1/chart")
async def chart_upgrade(value: ChartValue):
    logger.info(value)
    try:
        result = Chart(value).upgrade()
        return result
    except ChartError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.delete("/tink/v1.1/chart")
async def chart_uninstall(value: ChartValue):
    logger.info(value)
    try:
        result = Chart(value).uninstall()
        return result
    except ChartError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/tink/v1.1/charts")
async def chart_list(value: ChartValue):
    logger.info(value)
    try:
        result = Chart(value).list()
        return result
    except ChartError as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')


@app.get("/tink/v1.1/pod")
async def pod_list(value: PodValue):
    logger.info(value)
    try:
        result = api_instance.read_namespaced_pod(
            name=f'{value.type}-{value.uid}',
            namespace=NAMESPACE
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


@app.delete("/tink/v1.1/pod")
async def pod_delete(value: PodValue):
    logger.info(value)
    try:
        result = api_instance.delete_namespaced_pod(
            name=f'{value.type}-{value.uid}',
            namespace=NAMESPACE
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


@app.post("/tink/v1.1/pod/exec")
async def exec(value: PodValue):
    logger.info(value)
    try:
        exec_command = [
            '/bin/sh',
            '-c',
            value.cmd
        ]
        resp = stream(
            api_instance.connect_get_namespaced_pod_exec,
            f'{value.type}-{value.uid}',
            NAMESPACE,
            command=exec_command,
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


@app.patch("/tink/v1.1/pod/configmap")
async def configmap_update(value: PodValue):
    logger.info(value)
    try:
        testbed = value.configmap.testbed
        testcases = value.configmap.testcases
        data = {

            'testbed.yaml': AsLiteral(yaml.dump(testbed)),
            'testcases.yaml': AsLiteral(yaml.dump(testcases))
        }
        resp = api_instance.patch_namespaced_config_map(
            name=f'{value.type}-{value.uid}',
            namespace=NAMESPACE,
            body={'data': data}
        ).to_dict()
        logger.info(resp)
        return resp
    except ApiException as e:
        logger.error(e.body)
        raise HTTPException(status_code=e.status, detail=e.reason)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail='内部错误')
