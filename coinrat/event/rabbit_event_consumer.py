import json
import logging
import threading
import traceback

import pika

from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.domain import deserialize_datetime_interval, DateTimeFactory, DateTimeInterval
from coinrat.domain.pair import deserialize_pair
from coinrat.domain.order import deserialize_order
from coinrat.domain.candle import deserialize_candle_size, Candle, CandleStorage
from coinrat.event.event_types import EVENT_LAST_CANDLE_UPDATED, EVENT_NEW_ORDER, EVENT_NEW_STRATEGY_RUN
from coinrat.server.subscription_storage import SubscriptionStorage, LastCandleSubscription, NewOrderSubscription, \
    NewStrategyRunSubscription
from coinrat.server.socket_server import SocketServer
from coinrat.thread_watcher import ThreadWatcher

# Some synchronizers are not good enough to provide real-time data, therefore candles are missing
# This constant should be enough. If RabbitConsumer keeps crashing on:
#       AssertionError: Its expected to found candles after getting candle-added event. But none found.
# you probably need to fix synchronizer, because data from it are to much delayed.
from coinrat.domain.strategy import deserialize_strategy_run

SAFETY_MULTIPLIER = 10

logger = logging.getLogger(__name__)


class RabbitEventConsumer(threading.Thread):
    def __init__(
        self,
        thread_watcher: ThreadWatcher,
        rabbit_connection: pika.BlockingConnection,
        socket_server: SocketServer,
        subscription_storage: SubscriptionStorage,
        candle_storage_plugins: CandleStoragePlugins,
        datetime_factory: DateTimeFactory
    ):
        super().__init__()

        self._thread_watcher = thread_watcher
        self._datetime_factory = datetime_factory
        self._candle_storage_plugins = candle_storage_plugins
        self._subscription_storage = subscription_storage
        self._socket_server = socket_server
        self._channel = rabbit_connection.channel()
        self._channel.queue_declare(queue='events')

        self.register_callbacks_for_socket_server()
        self.register_callback_for_rabbit()

    def register_callback_for_rabbit(self):
        def rabbit_message_callback(ch, method, properties, body) -> None:
            try:
                return self._process_event_message(body)
            except Exception as e:
                self._channel.stop_consuming()
                self._channel.close()
                traceback.print_exc()
                self._thread_watcher.notify_exception(e)

        self._channel.basic_consume(rabbit_message_callback, queue='events', no_ack=True)

    def register_callbacks_for_socket_server(self):
        def on_subscribe(session_id, data):
            if data['event'] == EVENT_LAST_CANDLE_UPDATED:
                subscription = LastCandleSubscription(
                    session_id,
                    data['storage'],
                    data['market'],
                    deserialize_pair(data['pair']),
                    deserialize_candle_size(data['candle_size'])
                )
            elif data['event'] == EVENT_NEW_ORDER:
                subscription = NewOrderSubscription(
                    session_id,
                    data['storage'],
                    data['market'],
                    deserialize_pair(data['pair']),
                    deserialize_datetime_interval(data['interval'])
                )
            elif data['event'] == EVENT_NEW_STRATEGY_RUN:
                subscription = NewStrategyRunSubscription(session_id)
            else:
                raise ValueError('Event "{}" not supported'.format(data['event']))

            self._subscription_storage.subscribe(subscription)
            return 'OK'

        def on_unsubscribe(session_id, data):
            self._subscription_storage.unsubscribe(data['event'], session_id)
            return 'OK'

        self._socket_server.register_subscribes(on_subscribe, on_unsubscribe)

    def run(self):
        self._channel.start_consuming()

    def _find_last_candle_for_subscription(
        self,
        candle_storage: CandleStorage,
        subscription: LastCandleSubscription
    ) -> Candle:
        since = self._datetime_factory.now() - SAFETY_MULTIPLIER * subscription.candle_size.get_as_time_delta()
        interval = DateTimeInterval(since, None)
        candles = candle_storage.find_by(
            market_name=subscription.market_name,
            pair=subscription.pair,
            interval=interval,
            candle_size=subscription.candle_size
        )
        assert candles != [], 'Its expected to found candles after getting candle-added event. But none found.'
        return candles[-1]

    def _process_event_message(self, message_body):
        event_data = json.loads(message_body.decode("utf-8"))

        event_name = event_data['event']
        subscriptions = self._subscription_storage.find_subscriptions_for_event(event_name, event_data=event_data)

        if not subscriptions:
            logger.info('[Rabbit] Event "%s", received -> NO SUBSCRIPTIONS | %r', event_name, event_data)
            return

        if event_name == EVENT_LAST_CANDLE_UPDATED:
            candle_storage = self._candle_storage_plugins.get_candle_storage(event_data['storage'])
            for subscription in subscriptions:  # type: LastCandleSubscription
                candle = self._find_last_candle_for_subscription(candle_storage, subscription)
                self._socket_server.emit_last_candle(subscription.session_id, candle)

        elif event_name == EVENT_NEW_ORDER:
            for subscription in subscriptions:
                order = deserialize_order(event_data['order'])
                portfolio_snapshot_raw = event_data['order']['portfolio_snapshot']
                self._socket_server.emit_new_order(subscription.session_id, order, portfolio_snapshot_raw)

        elif event_name == EVENT_NEW_STRATEGY_RUN:
            for subscription in subscriptions:
                strategy_run = deserialize_strategy_run(event_data['strategy_run'])
                self._socket_server.emit_new_strategy_run(subscription.session_id, strategy_run)

        else:
            logger.info('[Rabbit] Event "%s", received -> NOT SUPPORTED | %r', event_name, event_data)
