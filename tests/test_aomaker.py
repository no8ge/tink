import json
import time
import uuid
import pytest
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestAomaker():

    # uid = f'{uuid.uuid4()}'
    uid = '091143e5-464e-4704-8438-04ecc98f4b1a'

    payload = {
        "type": "aomaker",
        "name": f'aomaker-{uid}',
        "uid": f'{uid}',
        'container': {
            'image': 'dockerhub.qingcloud.com/listen/hpc:4.0',
            'command': 'arun -e testbm -m hpc_fs',
        },
        'prefix': '/data/autotest/reports'
    }

    name = payload['name']

    def test_create_aomaker(self):
        resp = self.bs.post(
            f'{self.url}/tink/job',
            json=self.payload,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_get_job(self):
        while True:
            resp = self.bs.get(
                f'{self.url}/tink/job/{self.name}',
            )
            status = resp.json()['status']['phase']
            pprint(status)
            if status == 'Succeeded':
                break
            time.sleep(3)
        assert resp.status_code == 200

    def test_msg(self):
        payload = {
            'index': 'atop',
            'key_words': {
                'pod.name': self.name,
                'container.name': 'aomaker',
            },
            "from_": 0,
            "size": 20,
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
                'kubernetes.labels.uid': self.uid
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
        pprint(resp.json())
        assert resp.status_code == 200

        while True:
            resp = self.bs.get(
                f'{self.url}/files/tasks/{self.name}',
            )
            pprint(resp.json())
            if resp.json()['status'] == 'completed':
                break
            time.sleep(1)
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            f'{self.url}/files/',
            params={
                "prefix": f"{self.name}/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            }
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_delete_job(self):
        resp = self.bs.delete(
            f'{self.url}/tink/job/{self.name}'
        )
        pprint(resp.json())
        assert resp.status_code == 200
