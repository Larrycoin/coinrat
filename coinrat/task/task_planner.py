import json
import pika
from typing import Dict

from .task_types import TASK_REPLY_STRATEGY


class TaskPlanner:
    def __init__(self, rabbit_connection: pika.BlockingConnection) -> None:
        super().__init__()
        self.channel = rabbit_connection.channel()
        self.channel.queue_declare(queue='tasks')

    def plan_replay_strategy(self, data: Dict) -> None:
        self.channel.basic_publish(exchange='', routing_key='tasks', body=json.dumps({
            'task': TASK_REPLY_STRATEGY,
            'data': data,
        }))
