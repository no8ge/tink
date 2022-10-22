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
