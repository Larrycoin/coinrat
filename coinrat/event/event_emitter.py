import json
from typing import List

import pika

from coinrat.server.candle import serialize_candle
from coinrat.domain.candle import MinuteCandle
from .event_types import EVENT_NEW_CANDLE


class EventEmitter:
    def __init__(self, rabbit_connection: pika.BlockingConnection) -> None:
        super().__init__()
        self.channel = rabbit_connection.channel()
        self.channel.queue_declare(queue='events')

    def emit_new_candles(self, candles: List[MinuteCandle]) -> None:
        for candle in candles:
            self.channel.basic_publish(exchange='', routing_key='events', body=json.dumps({
                'event': EVENT_NEW_CANDLE,
                'data': serialize_candle(candle)
            }))
