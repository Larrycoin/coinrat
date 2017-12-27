import threading

import eventlet.wsgi
import os
import socketio
from flask import Flask

from coinrat.domain import DateTimeFactory
from coinrat.domain.candle import CandleStorage
from .pair import parse_pair
from .interval import parse_interval
from .candle import serialize_candles, MinuteCandle

EVENT_PING_REQUEST = 'ping_request'
EVENT_PING_RESPONSE = 'ping_response'
EVENT_GET_CANDLES = 'get_candles'
EVENT_NEW_CANDLES = 'new_candles'


class SocketServer(threading.Thread):

    def __init__(self, datetime_factory: DateTimeFactory, candle_storage: CandleStorage):
        super().__init__()

        self.sio = socketio.Server()

        @self.sio.on('connect')
        def connect(sid, environ):
            print("connect ", sid)

        @self.sio.on(EVENT_PING_REQUEST)
        def ping_request(sid, data):
            data['response_timestamp'] = datetime_factory.now().timestamp()
            self.sio.emit(EVENT_PING_RESPONSE, data)

        @self.sio.on(EVENT_GET_CANDLES)
        def candles(sid, data):
            result_candles = candle_storage.find_by(
                data['market_name'],
                parse_pair(data['pair']),
                parse_interval(data['interval'])
            )

            return 'OK', serialize_candles(result_candles)

        @self.sio.on('disconnect')
        def disconnect(sid):
            print('disconnect ', sid)

    def emit_new_candle(self, candle: MinuteCandle):
        self.sio.emit(EVENT_NEW_CANDLES, serialize_candles([candle]))

    def run(self):
        app = socketio.Middleware(self.sio, Flask(__name__))
        eventlet.wsgi.server(eventlet.listen((
            os.environ.get('SOCKET_SERVER_HOST'),
            int(os.environ.get('SOCKET_SERVER_PORT')),
        )), app)
