import uuid
import json
import pytest
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestHatbox():
    uid = '091143e5-464e-4704-8438-04ecc98f4b1a'

    payload = {
        "uid": uid,
        "name": 'test',
        "type": "hatbox",
        'container': {
            'image': 'dockerhub.qingcloud.com/qingtest/hatbox_base:1.0.1',
            'command': 'python HATengine.py case -m 2 -t 3 -s test_auto_create_case_step',
            'report': '/hatbox/Log/report/pytest_html',
        },
        'configmap': {
            'testbed': {'setup.ilm.enabled': '8'},
            'testcases': {'setup.ilm.enabled': '7'}
        },
    }

    header = {
        "Authorization": "admin"
    }

    def test_install_chart(self):
        resp = self.bs.post(
            f'/{self.env}/tink/v1.1/chart',
            json=self.payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_upgrade_chart(self):
        resp = self.bs.patch(
            f'/{self.env}/tink/v1.1/chart',
            json=self.payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_uninstall_chart(self):
        resp = self.bs.delete(
            f'/{self.env}/tink/v1.1/chart',
            json=self.payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_list_chart(self):
        resp = self.bs.get(
            f'/{self.env}/tink/v1.1/charts',
            json=self.payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_pod(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "hatbox",
        }
        resp = self.bs.get(
            f'/{self.env}/tink/v1.1/pod',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_delete_pod(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "hatbox",
        }
        resp = self.bs.delete(
            f'/{self.env}/tink/v1.1/pod',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_exec(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "hatbox",
            'cmd': 'echo 123'
        }
        resp = self.bs.post(
            f'/{self.env}/tink/v1.1/pod/exec',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_update_configmap(self):
        payload = {
            "uid": self.uid,
            "name": 'test',
            "type": "hatbox",
            'configmap': {
                'testbed': {'setup.ilm.enabled': '1'},
                'testcases': {'setup.ilm.enabled': '2'}
            },
        }
        resp = self.bs.patch(
            f'/{self.env}/tink/v1.1/pod/configmap',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_msg(self):
        label = self.payload['type'] + '-' + self.payload['uid']
        payload = {
            'index': 'logs',
            'key_words': {
                'kubernetes.labels.app': label,
            },
            "from_": 0,
            "size": 20,
        }

        resp = self.bs.post(
            f'/{self.env}/analysis/raw',
            headers=self.header,
            json=payload
        )
        pprint(resp.json())
        assert resp.status_code == 200

        payload = {
            'index': 'logs',
            'key_words': {
                'kubernetes.labels.app': label,
            },
            "from_": 0,
            "size": 20,
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
        payload = {
            "uid": self.uid,
            "type": self.payload['type'],
            'path': self.payload['container']['report']
        }
        resp = self.bs.get(
            f'/{self.env}/files/v1.1/report',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_object(self):
        resp = self.bs.get(
            f'/{self.env}/files/v1.1',
            params={
                "prefix": f"{self.payload['type']}-{self.uid}/hatbox/Log/report/pytest_html/widgets/summary.json",
                'bucket_name': 'result'
            },
            headers=self.header
        )
        assert resp.status_code == 200
