import logging
import threading
import os
import socketio
from flask import Flask

from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.domain import DateTimeFactory
from coinrat.domain import Pair
from coinrat.order_storage_plugins import OrderStoragePlugins
from .order import serialize_orders
from .interval import parse_interval
from .candle import serialize_candles, MinuteCandle, serialize_candle

EVENT_PING_REQUEST = 'ping_request'
EVENT_PING_RESPONSE = 'ping_response'

EVENT_GET_CANDLES = 'get_candles'
EVENT_NEW_CANDLES = 'new_candles'

EVENT_GET_ORDERS = 'get_orders'
EVENT_NEW_ORDERS = 'new_orders'

EVENT_SUBSCRIBE = 'subscribe'
EVENT_UNSUBSCRIBE = 'unsubscribe'


class SocketServer(threading.Thread):

    def __init__(
        self,
        datetime_factory: DateTimeFactory,
        candle_storage_plugins: CandleStoragePlugins,
        orders_storage_plugins: OrderStoragePlugins
    ):
        super().__init__()
        socket = socketio.Server(async_mode='threading')

        @socket.on('connect')
        def connect(sid, environ):
            print("connect ", sid)

        @socket.on(EVENT_PING_REQUEST)
        def ping_request(sid, data):
            data['response_timestamp'] = datetime_factory.now().timestamp()
            socket.emit(EVENT_PING_RESPONSE, data)

        @socket.on(EVENT_GET_CANDLES)
        def candles(sid, data):
            if 'candles_storage' not in data:
                return 'ERROR', {'message': 'Missing "candle_storage" field in request.'}

            candle_storage = candle_storage_plugins.get_candle_storage(data['candles_storage'])
            result_candles = candle_storage.find_by(
                data['market_name'],
                Pair.from_string(data['pair']),
                parse_interval(data['interval'])
            )

            return 'OK', serialize_candles(result_candles)

        @socket.on(EVENT_GET_ORDERS)
        def orders(sid, data):
            if 'orders_storage' not in data:
                return 'ERROR', {'message': 'Missing "orders_storage" field in request.'}

            orders_storage = orders_storage_plugins.get_order_storage(data['orders_storage'])
            result_orders = orders_storage.find_by(
                data['market_name'],
                Pair.from_string(data['pair']),
                interval=parse_interval(data['interval'])
            )

            return 'OK', serialize_orders(result_orders)

        @socket.on('disconnect')
        def disconnect(sid):
            print('disconnect ', sid)

        self._socket = socket

    def emit_new_candle(self, candle: MinuteCandle):
        data = serialize_candle(candle)
        logging.info('EMITTING: {}, {}'.format(EVENT_NEW_CANDLES, data))
        self._socket.emit(EVENT_NEW_CANDLES, data)

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
