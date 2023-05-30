import json
import yaml
import subprocess
from loguru import logger
from yaml.resolver import BaseResolver

from src.env import NAMESPACE
from src.model import ChartValue


class AsLiteral(str):
    pass


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


class ChartError(Exception):
    def __init__(self, status, reason):
        super().__init__(status, reason)
        self.status = status
        self.reason = reason


class Chart():

    def __init__(self, value: ChartValue) -> None:
        self.value = value
        self.release = str(self.value.uid)
        if self.value.configmap != None:
            testbed = self.value.configmap.testbed
            testcases = self.value.configmap.testcases
            self.value.configmap.testbed = AsLiteral(yaml.dump(testbed))
            self.value.configmap.testcases = AsLiteral(yaml.dump(testcases))
            data = self.value.dict()
        if self.value.configmap == None:
            data = self.value.dict()
            del data['configmap']
        del data['uid']
        data = yaml.dump(data)
        with open(f'{self.release}.yaml', 'w') as f:
            f.write(data)

    def install(self):
        proc = subprocess.Popen(
            f'helm install {self.release} plugins/{self.value.type} -n {NAMESPACE}  -f {self.release}.yaml -o json ',
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        outs, errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs.decode('utf-8')
        if errs == '':
            outs = json.loads(outs)
            del outs['chart']
            del outs['manifest']
            resp = {'outs': outs, 'errs': errs}
            logger.info(resp)
            return resp
        else:
            logger.error(errs)
            raise ChartError(500, errs)

    def uninstall(self):
        proc = subprocess.Popen(
            f'helm uninstall {self.release} -n {NAMESPACE}',
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        outs, errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs.decode('utf-8')
        if errs == '':
            resp = {'outs': outs, 'errs': errs}
            logger.info(resp)
            return resp
        else:
            logger.error(errs)
            raise ChartError(500, errs)

    def upgrade(self):
        proc = subprocess.Popen(
            f'helm upgrade {self.release} plugins/{self.value.type} -f {self.release}.yaml -n {NAMESPACE} -o json',
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        outs, errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs.decode('utf-8')
        if errs == '':
            outs = json.loads(outs)
            del outs['chart']
            del outs['manifest']
            resp = {'outs': outs, 'errs': errs}
            logger.info(resp)
            return resp
        else:
            logger.error(errs)
            raise ChartError(500, errs)

    def list(self):
        proc = subprocess.Popen(
            f'helm list -n {NAMESPACE} -o json',
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        outs, errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs.decode('utf-8')
        if errs == '':
            outs = json.loads(outs)
            resp = {'outs': outs, 'errs': errs}
            logger.info(resp)
            return resp
        else:
            logger.error(errs)
            raise ChartError(500, errs)
