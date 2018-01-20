import json
from typing import List

import pika

from coinrat.domain.candle import Candle, serialize_candle
from coinrat.domain.order import Order
from coinrat.domain.order import serialize_order
from .event_types import EVENT_NEW_CANDLE, EVENT_NEW_ORDER


class EventEmitter:
    def __init__(self, rabbit_connection: pika.BlockingConnection) -> None:
        super().__init__()
        self.channel = rabbit_connection.channel()
        self.channel.queue_declare(queue='events')

    def emit_new_candles(self, candle_storage: str, candles: List[Candle]) -> None:
        for candle in candles:
            self.channel.basic_publish(exchange='', routing_key='events', body=json.dumps({
                'event': EVENT_NEW_CANDLE,
                'candle': serialize_candle(candle),
                'storage': candle_storage
            }))

    def emit_new_order(self, order_storage: str, order: Order):
        self.channel.basic_publish(exchange='', routing_key='events', body=json.dumps({
            'event': EVENT_NEW_ORDER,
            'order': serialize_order(order),
            'storage': order_storage,
        }))
