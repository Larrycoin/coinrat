import json
import logging
import pika

from typing import List, Dict

from coinrat.domain.candle import Candle, serialize_candle
from coinrat.domain.order import Order
from coinrat.domain.order import serialize_order
from .event_types import EVENT_LAST_CANDLE_UPDATED, EVENT_NEW_ORDER

logger = logging.getLogger(__name__)


class EventEmitter:
    def __init__(self, rabbit_connection: pika.BlockingConnection) -> None:
        super().__init__()
        self.channel = rabbit_connection.channel()
        self.channel.queue_declare(queue='events')

    def emit_new_candles(self, candle_storage: str, candles: List[Candle]) -> None:
        for candle in candles:
            self.emit_event({
                'event': EVENT_LAST_CANDLE_UPDATED,
                'candle': serialize_candle(candle),
                'storage': candle_storage,
            })

    def emit_new_order(self, order_storage: str, order: Order):
        self.emit_event({
            'event': EVENT_NEW_ORDER,
            'order': serialize_order(order),
            'storage': order_storage,
        })

    def emit_event(self, event: Dict) -> None:
        logger.debug('Emitting event: %s', event)
        self.channel.basic_publish(exchange='', routing_key='events', body=json.dumps(event))
