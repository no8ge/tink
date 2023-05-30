import json
import pytest
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestOk():

    id = 'lunz'
    uid = '091143e5-464e-4704-8438-04ecc98f4b1a'

    header = {
        "Authorization": "admin"
    }

    def test_create_aomaker(self):
        payload = {
            "type": "aomaker",
            "name": self.id,
            "uid": self.uid,
            'container': {
                'image': 'dockerhub.qingcloud.com/listen/hpc:4.0',
                'command': 'arun -e testbm -m hpc_fs',
            },
            'prefix': '/data/autotest/reports/html'
        }

        resp = self.bs.post(
            '/tink/job',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_job(self):
        resp = self.bs.get(
            f'/tink/job/{self.id}-{self.uid}',
            headers=self.header
        )
        status = resp.json()['status']['phase']
        pprint(status)
        assert resp.status_code == 200

    def test_msg(self):
        payload = {
            'index': 'logs',
            'key_words': {
                'pod.name': self.id,
                'container.name': 'aomaker',
                'labels.uid': self.uid
            },
            "from_": 0,
            "size": 200,
        }

        resp = self.bs.post(
            '/analysis/raw',
            headers=self.header,
            json=payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

        payload = {
            'index': 'logs',
            'key_words': {
                'pod.name': self.id,
                'container.name': 'aomaker',
                'labels.uid': self.uid
            },
            "from_": 0,
            "size": 200,
            "offset": resp.json()['offset']
        }

        ws = websocket.WebSocket()
        ws.connect(
            self.ws_url,
            header=self.header
        )
        ws.send(json.dumps(payload))
        resp = ws.recv()
        pprint(json.loads(resp))
        assert ws.status == 101

    def test_get_report(self):
        resp = self.bs.get(
            f'/files/report/result/aomaker/{self.id}-{self.uid}', headers=self.header)
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            '/files/',
            params={
                "prefix": "lunz-091143e5-464e-4704-8438-04ecc98f4b1a/data/autotest/reports/html/widgets/summary.json",
                'bucket_name': 'result'
            },
            headers=self.header)
        assert resp.status_code == 200

    def test_delete_job(self):
        resp = self.bs.delete(
            f'/tink/job/{self.id}-{self.uid}',
            headers=self.header
        )
        assert resp.status_code == 200
