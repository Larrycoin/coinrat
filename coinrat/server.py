import socketio

from coinrat.domain import DateTimeFactory

PING_REQUEST = 'ping_request'
PING_RESPONSE = 'ping_response'


def create_socket_io(datetime_factory: DateTimeFactory):
    sio = socketio.Server()

    @sio.on('connect')
    def connect(sid, environ):
        print("connect ", sid)

    @sio.on(PING_REQUEST)
    def ping_request(sid, data):
        data['response_timestamp'] = datetime_factory.now().timestamp()
        sio.emit(PING_RESPONSE, data)

    @sio.on('disconnect')
    def disconnect(sid):
        print('disconnect ', sid)

    return sio
