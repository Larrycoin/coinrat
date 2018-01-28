import json
import logging
import uuid
import pika

from typing import Dict

from coinrat.domain import DateTimeFactory, deserialize_datetime_interval
from coinrat.domain.pair import deserialize_pair
from coinrat.domain.strategy import StrategyRun, StrategyRunStorage
from coinrat.strategy_replayer import StrategyReplayer
from .task_types import TASK_REPLY_STRATEGY

logger = logging.getLogger(__name__)


class TaskConsumer:
    def __init__(
        self,
        rabbit_connection: pika.BlockingConnection,
        strategy_replayer: StrategyReplayer,
        date_time_factory: DateTimeFactory,
        strategy_run_storage: StrategyRunStorage
    ) -> None:
        super().__init__()
        self._strategy_run_storage = strategy_run_storage
        self._strategy_replayer = strategy_replayer
        self._date_time_factory = date_time_factory

        self._channel = rabbit_connection.channel()
        self._channel.queue_declare(queue='tasks')

        def rabbit_message_callback(ch, method, properties, body) -> None:
            decoded_body = json.loads(body.decode("utf-8"))
            task = decoded_body['task']
            if task == TASK_REPLY_STRATEGY:
                self.process_reply_strategy(decoded_body['data'])

            else:
                logger.info("[Rabbit] Task received -> not supported | %r", decoded_body)

        self._channel.basic_consume(rabbit_message_callback, queue='tasks', no_ack=True)

    def process_reply_strategy(self, data: Dict) -> None:
        logger.info("[Rabbit] Proceessing task: %s | %r", TASK_REPLY_STRATEGY, data)
        interval = deserialize_datetime_interval(data)
        strategy_run = StrategyRun(
            uuid.uuid4(),
            self._date_time_factory.now(),
            deserialize_pair(data['pair']),
            'mock',
            data['market_configuration'],
            data['strategy_name'],
            data['strategy_configuration'],
            interval,
            data['candles_storage'],
            data['orders_storage']
        )
        self._strategy_run_storage.save(strategy_run)
        self._strategy_replayer.run(strategy_run)

    def run(self):
        self._channel.start_consuming()
