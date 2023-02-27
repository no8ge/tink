import json
import aiohttp
import pytest
import asyncio
import websocket
from pprint import pprint


@pytest.mark.usefixtures('init')
class TestBm():

    id = 'lunz'
    index = 40

    header = {
        "Authorization": "admin"
    }

    def test_create_aomaker(self):
        async def main(payload):
            async with aiohttp.ClientSession() as session:
                async with session.post(f'{self.url}/tink/job', json=payload, headers=self.header) as response:
                    print("Status:", response.status)

        tasks = []
        loop = asyncio.get_event_loop()
        for i in range(self.index):
            payload = {
                "type": "aomaker",
                "name": self.id + str(i),
                "uid": str(i),
                'container': {
                    'image': 'dockerhub.qingcloud.com/listen/hpc:4.0',
                    'command': 'arun -e testbm -m hpc_fs',
                },
                'prefix': '/data/autotest/reports'
            }
            task = asyncio.ensure_future(main(payload))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))

    def test_get_job(self):
        for i in range(self.index):
            resp = self.bs.get(
                f'/tink/job/{self.id + str(i)}',
                headers=self.header
            )
            status = resp.json()['status']['phase']
            pprint(status)
            assert resp.status_code == 200

    def test_msg(self):
        for i in range(self.index):
            payload = {
                'index': 'logs',
                'key_words': {
                    'pod.name': self.id + str(i),
                    'container.name': 'aomaker',
                    'labels.uid': str(i)
                },
                "from_": 0,
                "size": 200,
            }

            resp = self.bs.post(
                '/analysis/raw',
                headers=self.header,
                json=payload
            )
            pprint(resp.json())
            assert resp.status_code == 200

            payload = {
                'index': 'logs',
                'key_words': {
                    'pod.name': self.id + str(i),
                    'container.name': 'aomaker',
                    'labels.uid': str(i)
                },
                "from_": 0,
                "size": 200,
                "offset": resp.json()['offset']
            }

            ws = websocket.WebSocket()
            ws.connect(
                self.ws_url,
                header=self.header
            )
            ws.send(json.dumps(payload))
            resp = ws.recv()
            pprint(json.loads(resp))
            assert ws.status == 101

    def test_get_report(self):
        for i in range(self.index):
            resp = self.bs.get(
                f'/files/report/result/aomaker/{self.id + str(i) + str(i)}', headers=self.header)
            assert resp.status_code == 200

    def test_delete_job(self):
        for i in range(self.index):
            resp = self.bs.delete(
                f'/tink/job/{self.id + str(i)}',
                headers=self.header
            )
            assert resp.status_code == 200
