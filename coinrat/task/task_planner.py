import json
import logging
import traceback
from typing import Dict
from pika.exceptions import ConnectionClosed

from .task_types import TASK_REPLY_STRATEGY

logger = logging.getLogger(__name__)


class TaskPlanner:
    def __init__(self, rabbit_connection_factory: callable, maximum_retries=3) -> None:
        super().__init__()
        self._rabbit_connection_factory = rabbit_connection_factory
        self._obtain_connection_and_create_channel()
        self._maximum_retries = maximum_retries

    def _obtain_connection_and_create_channel(self):
        self.channel = self._rabbit_connection_factory().channel()
        self.channel.queue_declare(queue='tasks')

    def plan_replay_strategy(self, data: Dict) -> None:
        self._publish({'task': TASK_REPLY_STRATEGY, 'data': data, })

    def _publish(self, data: Dict) -> None:
        retry = 0
        try:
            self.channel.basic_publish(exchange='', routing_key='tasks', body=json.dumps(data))
        except ConnectionClosed as e:
            if retry > self._maximum_retries:
                raise e

            logger.warning('ERROR: ConnectionClosed' + str(e))
            traceback.print_exc()

            self._obtain_connection_and_create_channel()
            self._publish(data)
