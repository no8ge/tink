import uuid
import json
import time
from loguru import logger


logger.add('/tink/logs/demo.log', format="{message}")
for i in range(0, 60):
    uid = str(uuid.uuid1())
    dict = {
        'type': 'attribute',
        'uuid': uid,
        'data': i
    }
    josn_str = json.dumps(dict)
    logger.info(josn_str)
    time.sleep(1)
