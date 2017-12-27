import threading
import pika

from .socket_server import SocketServer


class RabbitConsumer(threading.Thread):
    def __init__(self, rabbit_connection: pika.BlockingConnection, socket_server: SocketServer):
        super().__init__()

        self.socket_server = socket_server
        self.channel = rabbit_connection.channel()
        self.channel.queue_declare(queue='events')

        def rabbit_message_callback(ch, method, properties, body) -> None:
            print(" [x] Received %r" % body)

        self.channel.basic_consume(rabbit_message_callback, queue='events', no_ack=True)

    def run(self):
        self.channel.start_consuming()
