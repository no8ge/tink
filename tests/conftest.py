import os
import pytest

from requests_toolbelt.sessions import BaseUrlSession


env = os.getenv('ENV')
host = os.getenv('HOST')
url = f'http://{host}'

@pytest.fixture()
def init(request):
    bs = BaseUrlSession(base_url=url)
    request.cls.bs = bs
    request.cls.env = env
    request.cls.ws_url = f'ws://{host}/{env}/analysis/ws/raw'
