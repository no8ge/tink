import uuid
import random
from src.helper import EsHelper
from datetime import datetime
from src.env import ELASTICSEARCH_SERVICE_HOSTS


class TestEsHelper:

    es = EsHelper(ELASTICSEARCH_SERVICE_HOSTS)
    index = 'test'

    data = {
        'title': 'usa',
        'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm',
        'date': datetime.now()
    }

    def test_index(self):
        index = str(uuid.uuid4())[0:6]
        self.es.index(index)

    def test_get(self):
        id = random.randint(1, 1000)
        self.data['url'] = 'baidu.com'
        self.es.insert(self.index, id, self.data)
        self.es.get(self.index, id)
        self.es.update(self.index, id, self.data)
        self.es.delete(self.index, id)

    def test_search(self):
        self.es.search(self.index, {'title': 'usa'}, 0, 2)
