import uuid
import pytest


@pytest.mark.usefixtures('init')
class TestJob():

    id = str(uuid.uuid4())[0:6]
    payload = {
        "type": "aomaker",
        "name": "199999",
        'container': {
            'image': 'dockerhub.qingcloud.com/listen/hpc:2.0',
            'command': 'arun -e qingcloud --mt --dist-mark fs sw',
        },
        'prefix': '/data/autotest/reports'
    }
    payload = {
        "type": "locust",
        "name": "1",
        'container': {
            'image': 'mx2542/demo:latest',
            'command': 'locust \
                -f src/locustfile.py \
                -u 10 \
                -r 3 \
                --run-time 30s \
                --host http://demo.tink:8002 \
                --loglevel=DEBUG \
                --html=report.html \
                --web-host=0.0.0.0 \
                --web-port=9090 \
                --autostart \
                --autoquit=3'
        },
        'prefix': '/demo/report.html',
    }

    name = payload['name']

    header = {
        "Authorization": "admin"
    }

    def test_create_job(self):
        resp = self.bs.post(
            '/tink/job',
            json=self.payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_job(self):
        resp = self.bs.get(
            f'/tink/job/{self.name}',
            headers=self.header
        )
        assert resp.status_code == 200

    def test_delete_job(self):
        resp = self.bs.delete(
            f'/tink/job/{self.name}',
            headers=self.header
        )
        assert resp.status_code == 200
