import json
import logging
import threading
import pika

from coinrat.event.event_types import EVENT_NEW_CANDLE
from .candle import parse_candle
from .socket_server import SocketServer


class RabbitConsumer(threading.Thread):
    def __init__(self, rabbit_connection: pika.BlockingConnection, socket_server: SocketServer):
        super().__init__()

        self._socket_server = socket_server
        self._channel = rabbit_connection.channel()
        self._channel.queue_declare(queue='events')

        def rabbit_message_callback(ch, method, properties, body) -> None:
            print(" [x] Received %r" % body)
            logging.info(" [x] Received %r" % body)
            decoded_body = json.loads(body.decode("utf-8"))

            if decoded_body['event'] == EVENT_NEW_CANDLE:
                self._socket_server.emit_new_candle(parse_candle(decoded_body['data']))
            else:
                logging.error('Event {} not supported'.format(decoded_body['event']))

        self._channel.basic_consume(rabbit_message_callback, queue='events', no_ack=True)

    def run(self):
        self._channel.start_consuming()
