import socketio

from coinrat.domain import DateTimeFactory
from coinrat.domain.candle import CandleStorage
from .pair import parse_pair
from .interval import parse_interval
from .candle import serialize_candles

EVENT_PING_REQUEST = 'ping_request'
EVENT_PING_RESPONSE = 'ping_response'
EVENT_CANDLES = 'candles'


def create_socket_io(
    datetime_factory: DateTimeFactory,
    candle_storage: CandleStorage
):
    sio = socketio.Server()

    @sio.on('connect')
    def connect(sid, environ):
        print("connect ", sid)

    @sio.on(EVENT_PING_REQUEST)
    def ping_request(sid, data):
        data['response_timestamp'] = datetime_factory.now().timestamp()
        sio.emit(EVENT_PING_RESPONSE, data)

    @sio.on(EVENT_CANDLES)
    def candles(sid, data):
        result_candles = candle_storage.find_by(
            data['market_name'],
            parse_pair(data['pair']),
            parse_interval(data['interval'])
        )

        return 'OK', serialize_candles(result_candles)

    @sio.on('disconnect')
    def disconnect(sid):
        print('disconnect ', sid)

    return sio
