import os
import pytest

from requests_toolbelt.sessions import BaseUrlSession


env = os.getenv('ENV')
envs = {
    'loc': 'http://127.0.0.1:8003',
    'dev': 'http://atop.test:31694',
    'test': 'http://tink.test:31695',
    'production': 'http://tink.com:31696',
}


@pytest.fixture()
def init(request):
    url = envs[env]
    bs = BaseUrlSession(base_url=url)
    request.cls.bs = bs
    request.cls.url = url
    if env == 'dev':
        request.cls.ws_url = 'ws://atop.test:31694/analysis/ws/raw'
    if env == 'test':
        request.cls.ws_url = 'ws://tink.test:31695/analysis/ws/raw'
    if env == 'production':
        request.cls.ws_url = 'ws://tink.com:31696/analysis/ws/raw'
