import uuid
import pytest

@pytest.mark.usefixtures('init')
class TestJob():

    id = 'lunz'

    header = {
        "Authorization": "admin"
    }

    def test_create_konika(self):

        payload = {
            "type": "konika",
            "name": self.id,
            'container': {
                'image': 'mx2542/test:2.0',
                'command': '',
            },
            'prefix': 'auth'
        }

        resp = self.bs.post(
            '/tink/job',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_create_aomaker(self):

        payload = {
            "type": "aomaker",
            "name": self.id,
            "uid": str(uuid.uuid4()),
            'container': {
                'image': 'dockerhub.qingcloud.com/listen/hpc:4.0',
                'command': f'arun -e qingcloud -m hpc_fs',
            },
            'prefix': '/data/autotest/reports'
        }

        resp = self.bs.post(
            '/tink/job',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_create_jmeter(self):

        payload = {
            "type": "jmeter",
            "name": self.id,
            'container': {
                'image': 'mx2542/demo:latest',
                'command': 'apache-jmeter-5.4.3/bin/jmeter -n -t src/demo.jmx -l report/test.jtl -e -o report',
            },
            'prefix': '/demo/report'
        }

        resp = self.bs.post(
            '/tink/job',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_create_locust(self):

        payload = {
            "type": "locust",
            "name": self.id,
            'container': {
                'image': 'dockerhub.qingcloud.com/qingtest/demo:1.0',
                'command': 'locust \
                    -f src/locustfile.py \
                    -u 10 \
                    -r 3 \
                    --run-time 30s \
                    --host http://dev-demo.atop:8002 \
                    --loglevel=DEBUG \
                    --html=report.html \
                    --web-host=0.0.0.0 \
                    --web-port=9090 \
                    --autostart \
                    --autoquit=3'
            },
            'prefix': '/demo/report.html',
        }

        resp = self.bs.post(
            '/tink/job',
            json=payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_job(self):
        resp = self.bs.get(
            f'/tink/job/{self.id}',
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_jobs(self):
        resp = self.bs.get(
            f'/tink/jobs',
            headers=self.header,
            params={
                '_from': 0,
                'size': 2
            }
        )
        assert resp.status_code == 200

    def test_delete_job(self):
        resp = self.bs.delete(
            f'/tink/job/{self.id}',
            headers=self.header
        )
        assert resp.status_code == 200

    def test_metrics(self):
        resp = self.bs.get(
            '/tink/metrics',
            headers=self.header
        )
        assert resp.status_code == 200
