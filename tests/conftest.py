import os
import pytest
from requests import Session


host = os.getenv('HOST')


@pytest.fixture()
def init(request):
    bs = Session()
    bs.headers['apikey'] = 'admin'
    request.cls.bs = bs
    request.cls.url = f'http://{host}'
