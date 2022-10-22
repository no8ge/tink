import os
import pytest

from requests_toolbelt.sessions import BaseUrlSession


@pytest.fixture()
def init(request):
    envs = {
        'dev': 'http://127.0.0.1:8003',
        'test': 'http://tink.test:31695',
    }
    env = os.getenv('TEST_ENV')
    bs = BaseUrlSession(base_url=envs[env])
    request.cls.bs = bs
