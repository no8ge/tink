import json
import pytest
import websocket
from pprint import pprint
from loguru import logger


@pytest.mark.usefixtures('init')
class TestAomaker():

    payload = {
        "type": "aomaker",
        "name": 'test',
        "uid": '091143e5-464e-4704-8438-04ecc98f4b1a',
        'container': {
            'image': 'dockerhub.qingcloud.com/listen/hpc:4.0',
            'command': 'arun -e testbm -m hpc_fs',
        },
        'prefix': '/data/autotest/reports/html'
    }

    name = payload['name']

    def test_create_aomaker(self):
        resp = self.bs.post(
            f'{self.url}/tink/job',
            json=self.payload,
        )
        assert resp.status_code == 200

    def test_get_job(self):
        resp = self.bs.get(
            f'{self.url}/tink/job/{self.name}',
        )
        status = resp.json()['status']['phase']
        pprint(status)
        assert resp.status_code == 200

    def test_msg(self):
        payload = {
            'index': 'atop',
            'key_words': {
                'pod.name': self.name,
                'container.name': 'aomaker',
                # 'labels.uid': self.payload['uid']
            },
            "from_": 0,
            "size": 100,
        }

        resp = self.bs.post(
            f'{self.url}/analysis/raw',
            json=payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

        payload = {
            'index': 'logs',
            'key_words': {
                'kubernetes.labels.uid': self.payload['uid']
            },
            "from_": 0,
            "size": 200,
            "offset": resp.json()['offset']
        }

        ws = websocket.WebSocket()
        ws.connect(
            f'{self.ws_url}/analysis/ws/raw',
        )
        ws.send(json.dumps(payload))
        resp = ws.recv()
        pprint(json.loads(resp))
        assert ws.status == 101

    def test_get_report(self):
        resp = self.bs.get(
            f'{self.url}/files/report/result/aomaker/{self.name}',
        )
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            f'{self.url}/files/',
            params={
                "prefix": f"{self.name}/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            }
        )
        assert resp.status_code == 200

    def test_delete_job(self):
        resp = self.bs.delete(
            f'{self.url}/tink/job/{self.name}'
        )
        assert resp.status_code == 200

    def test_container_log(self):
        payload = {
            'pod': self.name,
            'container': 'aomaker',
            'tail_lines': 10,
        }

        resp = self.bs.get(
            f'{self.url}/tink/v1.1/pod/log',
            json=payload
        )
        result = resp.text.split("\\n")
        pprint(result)
        assert resp.status_code == 200
