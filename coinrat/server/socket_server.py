import logging
import threading
import os
import socketio
from flask import Flask

from coinrat.domain import DateTimeFactory
from coinrat.domain.candle import CandleStorage
from .pair import parse_pair
from .interval import parse_interval
from .candle import serialize_candles, MinuteCandle, serialize_candle

EVENT_PING_REQUEST = 'ping_request'
EVENT_PING_RESPONSE = 'ping_response'
EVENT_GET_CANDLES = 'get_candles'
EVENT_NEW_CANDLES = 'new_candles'


class SocketServer(threading.Thread):

    def __init__(self, datetime_factory: DateTimeFactory, candle_storage: CandleStorage):
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
            result_candles = candle_storage.find_by(
                data['market_name'],
                parse_pair(data['pair']),
                parse_interval(data['interval'])
            )

            return 'OK', serialize_candles(result_candles)

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
