import datetime
import json
import dateutil.parser
import logging
import threading
import pika

from typing import Dict

from coinrat.event.event_types import EVENT_NEW_CANDLE
from coinrat.server.interval import parse_interval
from coinrat.domain import DateTimeInterval
from .candle import parse_candle
from .socket_server import SocketServer


class RabbitEventConsumer(threading.Thread):
    def __init__(self, rabbit_connection: pika.BlockingConnection, socket_server: SocketServer):
        super().__init__()

        self._socket_server = socket_server
        self._channel = rabbit_connection.channel()
        self._channel.queue_declare(queue='events')

        self._subscribed_events = {}

        def on_subscribe(sid, data):
            if data['event'] == EVENT_NEW_CANDLE:
                self._subscribe_for_new_candle_event(data)

        def on_unsubscribe(sid, data):
            self._subscribed_events[data['event']] = None
            logging.info('Event {} unsubscribed.'.format(data['event']))

        socket_server.register_subscribes(on_subscribe, on_unsubscribe)

        def rabbit_message_callback(ch, method, properties, body) -> None:
            decoded_body = json.loads(body.decode("utf-8"))

            event = decoded_body['event']
            if self.is_event_subscribed(decoded_body):
                if event == EVENT_NEW_CANDLE:
                    candle = parse_candle(decoded_body['candle'])
                    self._socket_server.emit_new_candle(candle)
                else:
                    logging.info("[Rabbit] Event received -> not supported | %r", decoded_body)
            else:
                logging.info("[Rabbit] Event received -> no subscription | %r", decoded_body)

        self._channel.basic_consume(rabbit_message_callback, queue='events', no_ack=True)

    def is_event_subscribed(self, event_data: Dict):
        event_name = event_data['event']
        if event_name == EVENT_NEW_CANDLE:
            storage = event_data['candle_storage']
            market_name = event_data['candle']['market']
            pair = event_data['candle']['pair']
            candle_time = dateutil.parser.parse(event_data['candle']['time']).replace(tzinfo=datetime.timezone.utc)

            try:
                interval: DateTimeInterval = self._subscribed_events[event_name][storage][market_name][pair]
            except KeyError:
                return False

            return interval.contains(candle_time)

        return False

    def _subscribe_for_new_candle_event(self, data):
        subscription = {
            data['candle_storage']: {
                data['market']: {
                    data['pair']: parse_interval(data['interval'])
                }
            }
        }
        self._subscribed_events[data['event']] = subscription
        logging.info('Event {} subscribed: {} {} {} {}'.format(
            data['event'],
            data['candle_storage'],
            data['market'],
            data['pair'],
            data['interval'])
        )

    def run(self):
        self._channel.start_consuming()
