import json
from loguru import logger

from src.utils import yaml
from src.utils import exec_cmd

from src.model import ChartModel
from src.model import RepoModel


class Chart():

    def __init__(self, ct: ChartModel) -> None:

        self.release = ct.release
        self.chart = ct.chart
        self.repo = ct.repo
        self.namespace = ct.namespace
        self.version = ct.version
        self.value = ct.value

        if self.namespace != None:
            self._namespace_arg = f'-n {self.namespace}'
        else:
            self._namespace_arg = ''

        if self.version != None:
            self._version_arg = f'--version {self.version}'
        else:
            self._version_arg = ''

        if self.value != None:
            try:
                data = yaml.dump(self.value)
                with open(f'{self.release}-value.yaml', 'w') as f:
                    f.write(data)
                logger.info(f'create {self.release}-value.yaml success')
                self._value_arg = f'-f {self.release}-value.yaml'
            except Exception as e:
                logger.error(e)
        else:
            self._value_arg = ''

    def install(self):
        cmd = f'helm upgrade --install {self.release} {self.repo}/{self.chart} {self._version_arg} {self._namespace_arg} {self._value_arg} -o json '
        return exec_cmd(cmd, output='json')

    def uninstall(self):
        cmd = f'helm uninstall {self.release} {self._namespace_arg}'
        return exec_cmd(cmd)

    def upgrade(self):
        cmd = f'helm upgrade {self.release} {self.repo}/{self.chart} {self._version_arg} {self._value_arg} {self._namespace_arg} -o json'
        return exec_cmd(cmd, output='json')

    def list(self):
        cmd = f'helm list {self._namespace_arg} -o json'
        return exec_cmd(cmd, output='json')


class Repo():
    def __init__(self, ro: RepoModel) -> None:
        self.name = ro.name
        self.url = ro.url

    def add(self):
        cmd = f'helm repo add {self.name} {self.url}'
        return exec_cmd(cmd)

    def list(self):
        cmd = 'helm repo list -o json'
        return exec_cmd(cmd, output='json')

    def remove(self):
        cmd = f'helm repo remove {self.name}'
        return exec_cmd(cmd)

    def update(self):
        cmd = f'helm repo update {self.name}'
        return exec_cmd(cmd)
