import json
import time
import uuid
import pytest

from pprint import pprint


@pytest.mark.usefixtures('init')
class TestTink():

    uid = f'{uuid.uuid4()}'

    ct = {
        'release': 'test',
        'chart': 'demo',
        'repo': 'atop',
        'namespace': 'default',
        'version': None,
        'value': None
    }

    ro = {
        'name': 'test',
        'url': 'https://no8ge.github.io/chartrepo/'
    }

    def test_add_repo(self):
        resp = self.bs.post(
            f'{self.url}/v1.0/repo',
            json=self.ro,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_get_repo(self):
        resp = self.bs.get(
            f'{self.url}/v1.0/repo',
            json=self.ro,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_upgrade_repo(self):
        resp = self.bs.patch(
            f'{self.url}/v1.0/repo',
            json=self.ro,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_remove_repo(self):
        resp = self.bs.delete(
            f'{self.url}/v1.0/repo',
            json=self.ro,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_install_chart(self):
        resp = self.bs.post(
            f'{self.url}/v1.0/chart',
            json=self.ct,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_get_chart(self):
        resp = self.bs.get(
            f'{self.url}/v1.0/chart',
            json=self.ct,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_upgrade_chart(self):
        resp = self.bs.patch(
            f'{self.url}/v1.0/chart',
            json=self.ct,
        )
        pprint(resp.json())
        assert resp.status_code == 200

    def test_uninstall_chart(self):
        resp = self.bs.delete(
            f'{self.url}/v1.0/chart',
            json=self.ct,
        )
        pprint(resp.json())
        assert resp.status_code == 200
