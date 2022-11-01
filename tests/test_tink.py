import pytest


@pytest.mark.usefixtures('init')
class TestJob():

    payload = {
        "type": "aomaker",
        "name": "1",
        'container': {
            'image': 'dockerhub.qingcloud.com/listen/hpc:1.0',
            'command': 'arun -e qingcloud --mt --dist-mark fs sw',
            'volume_mounts': {
                'log_mount_path': '/data/autotest/logs',
                'report_mount_path': '/data/autotest/reports'
            }
        },
        'log_name': 'log.log',
        'project_id': 'hpc',
        'report_id': '2'
    }

    payload = {
        "type": "locust",
        "name": "3",
        'container': {
            'image': 'mx2542/demo:latest',
            'command': 'locust \
                -f src/locustfile.py \
                -u 10 \
                -r 3 \
                --run-time 30s \
                --host http://demo.tink:8002 \
                --logfile=chart/log.log \
                --loglevel=DEBUG \
                --html=chart/report.html \
                --web-host=0.0.0.0 \
                --web-port=9090 \
                --autostart \
                --autoquit=3',
            'volume_mounts': {
                'log_mount_path': '/demo/chart',
                'report_mount_path': '/demo/chart'
            }
        },
        'log_name': 'log.log',
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


@pytest.mark.usefixtures('init')
class TestPod():

    payload = {
        "type": "demo",
        "name": "1",
        'container': {
            "image": 'mx2542/tink:latest',
            'command': 'python demo/test_demo.py',
            'volume_mounts': {
                'log_mount_path': '/tink/logs',
            }
        },
        'log_name': 'demo.log',
    }

    payload = {
        "type": "locust",
        "name": "3",
        'container': {
            'image': 'mx2542/demo:latest',
            'command': 'locust \
                -f src/locustfile.py \
                -u 10 \
                -r 3 \
                --run-time 30s \
                --host http://demo.tink:8002 \
                --logfile=chart/log.log \
                --loglevel=DEBUG \
                --html=chart/report.html \
                --web-host=0.0.0.0 \
                --web-port=9090 \
                --autostart \
                --autoquit=3',
            'volume_mounts': {
                'log_mount_path': '/demo/chart',
                'report_mount_path': '/demo/chart'
            }
        },
        'log_name': 'log.log',
    }

    name = payload['name']

    header = {
        "Authorization": "admin"
    }

    def test_create_pod(self):
        resp = self.bs.post(
            '/tink/pod',
            json=self.payload,
            headers=self.header
        )
        assert resp.status_code == 200

    def test_get_pod(self):
        resp = self.bs.get(
            f'/tink/pod/{self.name}',
            headers=self.header
        )
        assert resp.status_code == 200

    def test_delete_pod(self):
        resp = self.bs.delete(
            f'/tink/pod/{self.name}',
            headers=self.header
        )
        assert resp.status_code == 200
