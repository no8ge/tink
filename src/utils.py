import yaml
import json
import subprocess
from typing import List
from fastapi import WebSocket
from loguru import logger
from yaml.resolver import BaseResolver

from src.error import HelmError


class AsLiteral(str):
    pass


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


def represent_literal(dumper, data):
    return dumper.represent_scalar(
        BaseResolver.DEFAULT_SCALAR_TAG,
        data,
        style="|"
    )


yaml.add_representer(
    AsLiteral,
    represent_literal
)


def exec_cmd(cmd, output=None):
    try:
        logger.info(f'command: {cmd}')
        proc = subprocess.Popen(
            cmd,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        outs, errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs.decode('utf-8')
        if 'Error' in errs:
            logger.error(errs)
            raise HelmError(500, errs)
        if output == 'json':
            outs = json.loads(outs)
        resp = {'outs': outs, 'errs': errs}
        logger.info(resp)
        return resp
    except subprocess.CalledProcessError as e:
        logger.error(e)
        raise
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON format. Details: {e}')
        raise
