import datetime
import json
import logging
import threading
import pika

from typing import Dict

from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.domain import deserialize_datetime_interval, deserialize_pair
from coinrat.domain.candle import deserialize_candle
from coinrat.domain.order import deserialize_order
from coinrat.event.event_types import EVENT_LAST_CANDLE_UPDATED, EVENT_NEW_ORDER
from coinrat.server.subscription_storage import SubscriptionStorage, LastCandleSubscription, NewOrderSubscription
from coinrat.server.socket_server import SocketServer


class RabbitEventConsumer(threading.Thread):
    def __init__(
        self,
        rabbit_connection: pika.BlockingConnection,
        socket_server: SocketServer,
        subscription_storage: SubscriptionStorage,
        candle_storage_plugins: CandleStoragePlugins
    ):
        super().__init__()

        self._candle_storage_plugins = candle_storage_plugins
        self._subscription_storage = subscription_storage
        self._socket_server = socket_server
        self._channel = rabbit_connection.channel()
        self._channel.queue_declare(queue='events')

        def on_subscribe(session_id, data):
            if data['event'] == EVENT_LAST_CANDLE_UPDATED:
                subscription = LastCandleSubscription(
                    session_id,
                    data['storage'],
                    data['market'],
                    deserialize_pair(data['pair'])
                )
            elif data['event'] == EVENT_NEW_ORDER:
                subscription = NewOrderSubscription(
                    session_id,
                    data['storage'],
                    data['market'],
                    deserialize_pair(data['pair']),
                    deserialize_datetime_interval(data['interval'])
                )
            else:
                raise ValueError('Event "{}" not supported'.format(data['event']))

            self._subscription_storage.subscribe(subscription)

        def on_unsubscribe(session_id, data):
            self._subscription_storage.unsubscribe(session_id, data['event'])

        socket_server.register_subscribes(on_subscribe, on_unsubscribe)

        def rabbit_message_callback(ch, method, properties, body) -> None:
            event_data = json.loads(body.decode("utf-8"))

            event_name = event_data['event']
            subscriptions = self._subscription_storage.find_subscriptions_for_event(event_name, event_data=event_data)

            if event_name == EVENT_LAST_CANDLE_UPDATED:
                candle_storage = self._candle_storage_plugins.get_candle_storage(event_data['storage'])
                for subscription in subscriptions:
                    candle = candle_storage.find_by()[0]  # Todo: implemnt getting correctly sized last candle
                    self._socket_server.emit_last_candle(subscription.session_id, candle)

            if event_name == EVENT_NEW_ORDER:
                for subscription in subscriptions:
                    order = deserialize_order(event_data['order'])
                    self._socket_server.emit_new_order(subscription.session_id, order)

            else:
                logging.info("[Rabbit] Event received -> not supported | %r", event_data)

        self._channel.basic_consume(rabbit_message_callback, queue='events', no_ack=True)

    def run(self):
        self._channel.start_consuming()
