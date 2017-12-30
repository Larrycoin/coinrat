import os
import pika

from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.event.event_emitter import EventEmitter
from coinrat.market_plugins import MarketPlugins
from coinrat.order_storage_plugins import OrderStoragePlugins
from coinrat.server.rabbit_consumer import RabbitEventConsumer
from coinrat.server.socket_server import SocketServer
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.synchronizer_plugins import SynchronizerPlugins
from coinrat.domain import CurrentUtcDateTimeFactory, DateTimeFactory
from coinrat.task.task_planner import TaskPlanner
from coinrat.task.task_consumer import TaskConsumer


class DiContainer:
    def __init__(self) -> None:
        super().__init__()
        self._storage = {
            'candle_storage_plugins': {
                'instance': None,
                'factory': lambda: CandleStoragePlugins(),
            },
            'order_storage_plugins': {
                'instance': None,
                'factory': lambda: OrderStoragePlugins(),
            },
            'market_plugins': {
                'instance': None,
                'factory': lambda: MarketPlugins(),
            },
            'synchronizer_plugins': {
                'instance': None,
                'factory': lambda: SynchronizerPlugins(),
            },
            'strategy_plugins': {
                'instance': None,
                'factory': lambda: StrategyPlugins(),
            },
            'rabbit_connection': {
                'instance': None,
                'factory': lambda: pika.BlockingConnection(
                    pika.ConnectionParameters(os.environ.get('RABBITMQ_SERVER_HOST')),
                )
            },
            'event_emitter': {
                'instance': None,
                'factory': lambda: EventEmitter(self.rabbit_connection),
            },
            'task_planner': {
                'instance': None,
                'factory': lambda: TaskPlanner(self.rabbit_connection),
            },
            'datetime_factory': {
                'instance': None,
                'factory': lambda: CurrentUtcDateTimeFactory(),
            },
            'socket_server': {
                'instance': None,
                'factory': lambda: SocketServer(
                    self.task_planner,
                    self.datetime_factory,
                    self.candle_storage_plugins,
                    self.order_storage_plugins
                ),
            },
            'rabbit_event_consumer': {
                'instance': None,
                'factory': lambda: RabbitEventConsumer(self.rabbit_connection, self.socket_server)
            },
            'task_consumer': {
                'instance': None,
                'factory': lambda: TaskConsumer(
                    self.rabbit_connection,
                    self.candle_storage_plugins,
                    self.order_storage_plugins,
                    self.strategy_plugins, self.market_plugins
                ),
            }
        }

    def _get(self, name: str):
        if self._storage[name]['instance'] is None:
            self._storage[name]['instance'] = self._storage[name]['factory']()

        return self._storage[name]['instance']

    @property
    def candle_storage_plugins(self) -> CandleStoragePlugins:
        return self._get('candle_storage_plugins')

    @property
    def order_storage_plugins(self) -> OrderStoragePlugins:
        return self._get('order_storage_plugins')

    @property
    def market_plugins(self) -> MarketPlugins:
        return self._get('market_plugins')

    @property
    def synchronizer_plugins(self) -> SynchronizerPlugins:
        return self._get('synchronizer_plugins')

    @property
    def strategy_plugins(self) -> StrategyPlugins:
        return self._get('strategy_plugins')

    @property
    def socket_server(self) -> SocketServer:
        return self._get('socket_server')

    @property
    def rabbit_connection(self) -> pika.BlockingConnection:
        return self._get('rabbit_connection')

    @property
    def event_emitter(self) -> EventEmitter:
        return self._get('rabbit_connection')

    @property
    def task_planner(self) -> TaskPlanner:
        return self._get('task_planner')

    @property
    def datetime_factory(self) -> DateTimeFactory:
        return self._get('datetime_factory')

    @property
    def rabbit_event_consumer(self) -> RabbitEventConsumer:
        return self._get('rabbit_event_consumer')

    @property
    def task_consumer(self) -> TaskConsumer:
        return self._get('task_consumer')
