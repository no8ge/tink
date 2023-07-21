import time
import uuid
import json
import pytest
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestPluginAomaker():
    uid = '091143e5-464e-4704-8438-04ecc98f4b1a'
    # uid = f'{uuid.uuid4()}'

    payload = {
        "uid": uid,
        "name": 'test',
        "type": "aomaker",
        'container': {
            'image': 'dockerhub.qingcloud.com/qingtest/qke-cases:1.0.3',
            'command': 'pip install minio; arun -e qingcloud testcases/test_api/qke/test_cluster.py::TestCluster::test_describe_cluster_versions --region sh1 --zone sh1a',
            'report': '/data/autotest/reports',
        }
    }

    def test_install_chart(self):
        resp = self.bs.post(
            f'{self.url}/tink/v1.1/chart',
            json=self.payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_list_chart(self):
        resp = self.bs.get(
            f'{self.url}/tink/v1.1/charts',
            json=self.payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_upgrade_chart(self):
        resp = self.bs.patch(
            f'{self.url}/tink/v1.1/chart',
            json=self.payload
        )
        assert resp.status_code == 200

    def test_get_pod(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "aomaker",
        }
        while True:
            resp = self.bs.get(
                f'{self.url}/tink/v1.1/pod',
                json=payload
            )
            status = resp.json()['status']['phase']
            pprint(status)
            if status == 'Running':
                break
            time.sleep(3)
            assert resp.status_code == 200

    def test_update_configmap(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "aomaker",
            'configmap': {
                'testbed': {'setup.ilm.enabled': '1'},
                'testcases': {'setup.ilm.enabled': '2'}
            },
        }
        resp = self.bs.patch(
            f'{self.url}/tink/v1.1/pod/configmap',
            json=payload
        )
        assert resp.status_code == 200

    def test_exec(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "aomaker",
            'cmd': 'python /atop/cli.py'
        }
        resp = self.bs.post(
            f'{self.url}/tink/v1.1/pod/exec',
            json=payload
        )
        pprint(resp.text)
        assert resp.status_code == 200

    def test_msg(self):
        payload = {
            'index': 'logs',
            'key_words': {
                'log.file.path': f"/aomaker/Log/logs/aomaker-{self.uid}.log",
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
                'log.file.path': f"/aomaker/Log/logs/aomaker-{self.uid}.log",
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
        payload = {
            "uid": self.uid,
            "type": self.payload['type'],
            'path': self.payload['container']['report']
        }
        resp = self.bs.get(
            f'{self.url}/files/v1.1/report',
            json=payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            f'{self.url}/files/v1.1',
            params={
                "prefix": f"aomaker-{self.uid}/aomaker/Log/report/pytest_html/widgets/summary.json",
                'bucket_name': 'result'
            }
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_delete_pod(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "aomaker",
        }
        resp = self.bs.delete(
            f'{self.url}/tink/v1.1/pod',
            json=payload
        )
        assert resp.status_code == 200

        while True:
            resp = self.bs.get(
                f'{self.url}/tink/v1.1/pod',
                json=payload
            )
            pprint(resp.status_code)
            if resp.status_code == 404:
                break
            time.sleep(3)

    def test_uninstall_chart(self):
        resp = self.bs.delete(
            f'{self.url}/tink/v1.1/chart',
            json=self.payload
        )
        pprint(resp.json())
        assert resp.status_code == 200
