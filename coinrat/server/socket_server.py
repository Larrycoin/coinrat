import json
import logging
import threading
import os

import socketio
from flask import Flask

from coinrat.domain import DateTimeFactory, serialize_balances, deserialize_datetime_interval
from coinrat.domain.pair import deserialize_pair, serialize_pair
from coinrat.domain.order import Order, serialize_order, serialize_orders
from coinrat.domain.candle import serialize_candles, Candle, serialize_candle, deserialize_candle_size
from coinrat.order_storage_plugins import OrderStoragePlugins
from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.server.socket_event_types import EVENT_PING_REQUEST, EVENT_PING_RESPONSE, EVENT_GET_CANDLES, \
    EVENT_GET_ORDERS, EVENT_RUN_REPLY, EVENT_SUBSCRIBE, EVENT_UNSUBSCRIBE, EVENT_LAST_CANDLE_UPDATED, \
    EVENT_NEW_ORDERS, EVENT_CLEAR_ORDERS, EVENT_GET_MARKETS, EVENT_GET_PAIRS, EVENT_GET_CANDLE_STORAGES, \
    EVENT_GET_ORDER_STORAGES, EVENT_GET_STRATEGIES, SOCKET_EVENT_GET_BALANCE, EVENT_GET_STRATEGY_RUNS, \
    EVENT_NEW_STRATEGY_RUN
from coinrat.task.task_planner import TaskPlanner
from coinrat.market_plugins import MarketPlugins
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.domain.strategy import StrategyRunStorage, serialize_strategy_runs, StrategyRun, serialize_strategy_run

logger = logging.getLogger(__name__)


class SocketServer(threading.Thread):
    def __init__(
        self,
        task_planner: TaskPlanner,
        datetime_factory: DateTimeFactory,
        candle_storage_plugins: CandleStoragePlugins,
        order_storage_plugins: OrderStoragePlugins,
        market_plugins: MarketPlugins,
        strategy_plugins: StrategyPlugins,
        strategy_run_storage: StrategyRunStorage
    ):
        super().__init__()
        self.task_planner = task_planner
        socket = socketio.Server(async_mode='threading')

        @socket.on('connect')
        def connect(sid, environ):
            logger.info('Socket %s connected ', sid)

        @socket.on(EVENT_PING_REQUEST)
        def ping_request(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_PING_REQUEST, data))

            data['response_timestamp'] = datetime_factory.now().timestamp()
            socket.emit(EVENT_PING_RESPONSE, data)

        @socket.on(SOCKET_EVENT_GET_BALANCE)
        def balances(sid, data):
            logger.info('RECEIVED: {}, {}'.format(SOCKET_EVENT_GET_BALANCE, data))

            if 'market_name' not in data:
                return 'ERROR', {'message': 'Missing "market_name" field in request.'}

            market = market_plugins.get_market(data['market_name'], datetime_factory, {})

            return 'OK', serialize_balances(market.get_balances())

        @socket.on(EVENT_GET_CANDLES)
        def candles(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_CANDLES, data))

            if 'candle_storage' not in data:
                return 'ERROR', {'message': 'Missing "candle_storage" field in request.'}

            candle_storage = candle_storage_plugins.get_candle_storage(data['candle_storage'])
            result_candles = candle_storage.find_by(
                data['market'],
                deserialize_pair(data['pair']),
                deserialize_datetime_interval(data['interval']),
                candle_size=deserialize_candle_size(data['candle_size'])
            )

            return 'OK', serialize_candles(result_candles)

        @socket.on(EVENT_GET_MARKETS)
        def markets(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_MARKETS, data))

            result = []
            for market_name in market_plugins.get_available_markets():
                market_class = market_plugins.get_market_class(market_name)
                result.append({
                    'name': market_name,
                    'configuration_structure': market_class.get_configuration_structure(),
                })

            return 'OK', result

        @socket.on(EVENT_GET_PAIRS)
        def pairs(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_PAIRS, data))

            if 'market_name' not in data:
                return 'ERROR', {'message': 'Missing "market_name" field in request.'}

            market_name = data['market_name']
            market = market_plugins.get_market(market_name, datetime_factory, {})

            return 'OK', list(map(
                lambda pair: {
                    'key': serialize_pair(pair),
                    'name': pair.base_currency + '-' + pair.market_currency
                },
                market.get_all_tradable_pairs()
            ))

        @socket.on(EVENT_GET_CANDLE_STORAGES)
        def candle_storages(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_CANDLE_STORAGES, data))

            return 'OK', list(map(
                lambda storage_name: {'name': storage_name},
                candle_storage_plugins.get_available_candle_storages()
            ))

        @socket.on(EVENT_GET_ORDER_STORAGES)
        def order_storages(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_ORDER_STORAGES, data))

            return 'OK', list(map(
                lambda storage_name: {'name': storage_name},
                order_storage_plugins.get_available_order_storages()
            ))

        @socket.on(EVENT_GET_STRATEGIES)
        def strategies(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_STRATEGIES, data))

            result = []
            for market_name in strategy_plugins.get_available_strategies():
                strategy_class = strategy_plugins.get_strategy_class(market_name)
                result.append({
                    'name': market_name,
                    'configuration_structure': strategy_class.get_configuration_structure(),
                })

            return 'OK', result

        @socket.on(EVENT_GET_ORDERS)
        def orders(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_ORDERS, data))

            if 'order_storage' not in data:
                return 'ERROR', {'message': 'Missing "order_storage" field in request.'}

            order_storage = order_storage_plugins.get_order_storage(data['order_storage'])

            strategy_run_id = data['strategy_run_id'] if 'strategy_run_id' in data else None

            result_orders = order_storage.find_by(
                data['market'],
                deserialize_pair(data['pair']),
                interval=deserialize_datetime_interval(data['interval']),
                strategy_run_id=strategy_run_id
            )

            return 'OK', serialize_orders(result_orders)

        @socket.on(EVENT_GET_STRATEGY_RUNS)
        def strategy_runs(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_GET_STRATEGY_RUNS, data))
            return 'OK', serialize_strategy_runs(strategy_run_storage.find_by())

        @socket.on(EVENT_CLEAR_ORDERS)
        def clear_orders(sid, data):
            logger.info('RECEIVED: {}, {}'.format(EVENT_CLEAR_ORDERS, data))

            if 'order_storage' not in data:
                return 'ERROR', {'message': 'Missing "order_storage" field in request.'}

            order_storage = order_storage_plugins.get_order_storage(data['order_storage'])
            order_storage.delete_by(
                data['market'],
                deserialize_pair(data['pair']),
                interval=deserialize_datetime_interval(data['interval'])
            )

            return 'OK'

        @socket.on(EVENT_RUN_REPLY)
        def reply(sid, data):
            logger.info('Received Strategy REPLAY request: ' + json.dumps(data))
            self.task_planner.plan_replay_strategy(data)

            return 'OK'

        @socket.on('disconnect')
        def disconnect(sid):
            logger.info('Socket %s disconnect ', sid)

        self._socket = socket

    def emit_last_candle(self, session_id: str, candle: Candle):
        data = serialize_candle(candle)
        logger.info('EMITTING [session={}]: {}, {}'.format(session_id, EVENT_LAST_CANDLE_UPDATED, data))
        self._socket.emit(EVENT_LAST_CANDLE_UPDATED, data, room=session_id)

    def emit_new_order(self, session_id: str, order: Order):
        data = serialize_order(order)
        logger.info('EMITTING [session={}]: {}, {}'.format(session_id, EVENT_NEW_ORDERS, data))
        self._socket.emit(EVENT_NEW_ORDERS, data, room=session_id)

    def emit_new_strategy_run(self, session_id: str, strategy_run: StrategyRun):
        data = serialize_strategy_run(strategy_run)
        logger.info('EMITTING [session={}]: {}, {}'.format(session_id, EVENT_NEW_STRATEGY_RUN, data))
        self._socket.emit(EVENT_NEW_STRATEGY_RUN, data, room=session_id)

    def run(self):
        app = Flask(__name__)
        app.wsgi_app = socketio.Middleware(self._socket, app.wsgi_app)
        app.run(
            threaded=True,
            host=os.environ.get('SOCKET_SERVER_HOST'),
            port=int(os.environ.get('SOCKET_SERVER_PORT'))
        )

    def register_subscribes(self, on_subscribe: callable, on_unsubscribe: callable):
        self._socket.on(EVENT_SUBSCRIBE, on_subscribe)
        self._socket.on(EVENT_UNSUBSCRIBE, on_unsubscribe)
