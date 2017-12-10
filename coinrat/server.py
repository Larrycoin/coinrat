import socketio
import eventlet.wsgi
from flask import Flask

sio = socketio.Server()
app = Flask(__name__)


@sio.on('connect', namespace='/')
def connect(sid, environ):
    print("connect ", sid)
    sio.emit('event', room=sid)


@sio.on('event', namespace='/')
def message(sid, data):
    print("event ", data)
    sio.emit('event', room=sid)


@sio.on('disconnect', namespace='/chat')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('localhost', 8000)), app)
