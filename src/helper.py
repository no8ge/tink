from elasticsearch import Elasticsearch
from prometheus_client import CollectorRegistry, Gauge, generate_latest


class EsHelper():

    def __init__(self, host) -> None:
        self.host = host
        self.client = Elasticsearch(self.host)

    def index(self, index):
        result = self.client.indices.create(index=index, ignore=400)
        return result

    def insert(self, index, id, data):
        result = self.client.index(index=index, id=id, document=data)
        return result

    def get(self, index, id):
        result = self.client.get(index=index, id=id)
        return result

    def delete(self, index, id):
        result = self.client.delete(index=index, id=id)
        return result

    def update(self, index, id, doc):
        result = self.client.update(index=index, id=id, doc=doc)
        return result

    def search(self, index, key_words, _from, size, type='must', mod='term'):
        q = self.build_query(key_words, _from, size, type=type, mod=mod)
        result = self.client.search(index=index, body=q)
        return result

    def build_query(self, key_words, _from, size, type='must', mod='term'):
        q = {
            'query': {
                'bool': {}
            },
            "sort": [],
            "aggs": {
            }}
        q['from'] = _from
        q['size'] = size
        q['query']['bool'][type] = []
        for k, v in key_words.items():
            q['query']['bool'][type].append(
                {
                    mod: {
                        f'{k}.keyword': v}
                }
            )
        return q


class PrometheusHekper():

    def __init__(self) -> None:

        self.registry = CollectorRegistry()
        self.tink_task_status = Gauge(
            'tink_task_status',
            'pod status by tink created',
            ['name', 'type', 'status'],
            registry=self.registry
        )

    def generate_latest(self):
        return generate_latest(self.registry)
