import datetime
import json
import dateutil.parser
import logging
import threading
import pika

from typing import Dict

from coinrat.domain import DateTimeInterval, deserialize_datetime_interval
from coinrat.domain.candle import deserialize_candle
from coinrat.domain.order import deserialize_order
from coinrat.event.event_types import EVENT_NEW_CANDLE, EVENT_NEW_ORDER
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
                self._subscribe_for_new_entity_event(data)

            if data['event'] == EVENT_NEW_ORDER:
                self._subscribe_for_new_entity_event(data)

        def on_unsubscribe(sid, data):
            self._subscribed_events[data['event']] = None
            logging.info('Event {} unsubscribed.'.format(data['event']))

        socket_server.register_subscribes(on_subscribe, on_unsubscribe)

        def rabbit_message_callback(ch, method, properties, body) -> None:
            decoded_body = json.loads(body.decode("utf-8"))

            event = decoded_body['event']

            if event == EVENT_NEW_CANDLE:
                self.process_new_candle_event(decoded_body)

            if event == EVENT_NEW_ORDER:
                self.process_new_order_event(decoded_body)

            else:
                logging.info("[Rabbit] Event received -> not supported | %r", decoded_body)

        self._channel.basic_consume(rabbit_message_callback, queue='events', no_ack=True)

    def is_event_subscribed(self, event_name: str, storage: str, market: str, pair: str, time: str):
        try:
            interval: DateTimeInterval = self._subscribed_events[event_name][storage][market][pair]
        except KeyError:
            return False

        return interval.contains(dateutil.parser.parse(time).replace(tzinfo=datetime.timezone.utc))

    def _subscribe_for_new_entity_event(self, data):
        subscription = {
            data['storage']: {
                data['market']: {
                    data['pair']: deserialize_datetime_interval(data['interval'])
                }
            }
        }
        self._subscribed_events[data['event']] = subscription
        logging.info('Event {} subscribed: {} {} {} {}'.format(
            data['event'],
            data['storage'],
            data['market'],
            data['pair'],
            data['interval'])
        )

    def process_new_order_event(self, decoded_body: Dict) -> None:
        order = deserialize_order(decoded_body['order'])
        if self.is_event_subscribed(
            decoded_body['event'],
            decoded_body['storage'],
            decoded_body['order']['market'],
            decoded_body['order']['pair'],
            decoded_body['order']['created_at'],
        ):
            self._socket_server.emit_new_order(order)
        else:
            logging.info("[Rabbit] Event received -> no subscription | %r", decoded_body)

    def process_new_candle_event(self, decoded_body: Dict) -> None:
        candle = deserialize_candle(decoded_body['candle'])
        if self.is_event_subscribed(
            decoded_body['event'],
            decoded_body['storage'],
            decoded_body['candle']['market'],
            decoded_body['candle']['pair'],
            decoded_body['candle']['time'],
        ):
            self._socket_server.emit_new_candle(candle)
        else:
            logging.info("[Rabbit] Event received -> no subscription | %r", decoded_body)

    def run(self):
        self._channel.start_consuming()
