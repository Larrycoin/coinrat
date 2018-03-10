import logging
import os
import MySQLdb
import pika

from typing import Callable, Set, cast

import coinrat_mock
from coinrat.event.null_event_emitter import NullEventEmitter
from coinrat.event.rabbit_event_emitter import RabbitEventEmitter

from coinrat.portfolio_snapshot_storage_plugins import PortfolioSnapshotStoragePlugins
from .di_container import DiContainer
from coinrat.strategy_standard_runner import StrategyStandardRunner
from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.event.event_emitter import EventEmitter
from coinrat.market_plugins import MarketPlugins
from coinrat.order_storage_plugins import OrderStoragePlugins
from coinrat.event.rabbit_event_consumer import RabbitEventConsumer
from coinrat.server.socket_server import SocketServer
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.synchronizer_plugins import SynchronizerPlugins
from coinrat.domain import CurrentUtcDateTimeFactory, DateTimeFactory
from coinrat.domain.strategy import StrategyRunStorage
from coinrat.task.task_planner import TaskPlanner
from coinrat.task.task_consumer import TaskConsumer
from coinrat.strategy_replayer import StrategyReplayer
from coinrat.server.subscription_storage import SubscriptionStorage
from coinrat.thread_watcher import ThreadWatcher

logger = logging.getLogger(__name__)


class DiContainerCoinrat(DiContainer):

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
                'factory': self._create_market_plugins,
            },
            'synchronizer_plugins': {
                'instance': None,
                'factory': lambda: SynchronizerPlugins(),
            },
            'strategy_plugins': {
                'instance': None,
                'factory': lambda: StrategyPlugins(),
            },
            'portfolio_snapshot_storage_plugins': {
                'instance': None,
                'factory': lambda: PortfolioSnapshotStoragePlugins(),
            },
            'rabbit_connection': {
                'instance': None,
                'factory': self._create_rabbit_connection,
            },
            'event_emitter': {
                'instance': None,
                'factory': self._create_event_emitter,
            },
            'task_planner': {
                'instance': None,
                'factory': lambda: TaskPlanner(self._get_factory('rabbit_connection')),
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
                    self.order_storage_plugins,
                    self.market_plugins,
                    self.strategy_plugins,
                    self.strategy_run_storage,
                    self.portfolio_snapshot_storage_plugins
                ),
            },
            'strategy_replayer': {
                'instance': None,
                'factory': lambda: StrategyReplayer(
                    self.candle_storage_plugins,
                    self.order_storage_plugins,
                    self.strategy_plugins,
                    self.market_plugins,
                    self.portfolio_snapshot_storage_plugins,
                    self.event_emitter
                )
            },
            'task_consumer': {
                'instance': None,
                'factory': lambda: TaskConsumer(
                    self.rabbit_connection,
                    self.strategy_replayer,
                    self.datetime_factory,
                    self.strategy_run_storage,
                    self.event_emitter
                ),
            },
            'subscription_storage': {
                'instance': None,
                'factory': lambda: SubscriptionStorage(),
            },
            'mysql_connection': {
                'instance': None,
                'factory': lambda: MySQLdb.connect(
                    host=os.environ.get('MYSQL_HOST'),
                    database=os.environ.get('MYSQL_DATABASE'),
                    user=os.environ.get('MYSQL_USER'),
                    password=os.environ.get('MYSQL_PASSWORD'),
                ),
            },
            'strategy_run_storage': {
                'instance': None,
                'factory': lambda: StrategyRunStorage(self.mysql_connection),
            },
            'strategy_standard_runner': {
                'instance': None,
                'factory': lambda: StrategyStandardRunner(
                    self.candle_storage_plugins,
                    self.order_storage_plugins,
                    self.strategy_plugins,
                    self.market_plugins,
                    self.portfolio_snapshot_storage_plugins,
                    self.event_emitter,
                    self.datetime_factory,
                ),
            }
        }

    def _create_event_emitter(self) -> EventEmitter:
        event_emitter = os.environ.get('EVENT_EMITTER')

        assert event_emitter in ['rabbit', 'null'], 'Event-emitter must be configured to "rabbit" or "null".'

        if event_emitter == 'rabbit':
            return RabbitEventEmitter(self.rabbit_connection)

        return NullEventEmitter()

    @staticmethod
    def _create_rabbit_connection() -> pika.BlockingConnection:
        host = os.environ.get('RABBITMQ_SERVER_HOST')
        username = os.environ.get('RABBITMQ_USERNAME')

        logger.debug('Rabbit connection, user: {} host: {}'.format(username, host))

        credentials = pika.PlainCredentials(username, os.environ.get('RABBITMQ_PASSWORD'))

        return pika.BlockingConnection(pika.ConnectionParameters(host=host, credentials=credentials))

    @staticmethod
    def _create_market_plugins() -> MarketPlugins:
        market_plugins_service = MarketPlugins()

        markets: Set = set()
        for market_plugin in market_plugins_service.get_available_market_plugins():
            if market_plugin.get_name() != 'coinrat_mock':
                markets = markets.union(set(market_plugin.get_available_markets()))

        mock_plugin = cast(coinrat_mock.plugin.MarketPlugin, market_plugins_service.get_plugin('coinrat_mock'))
        mock_plugin.set_available_markets(list(markets))

        return market_plugins_service

    def _get_factory(self, name: str) -> Callable:
        return self._storage[name]['factory']

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
    def portfolio_snapshot_storage_plugins(self) -> PortfolioSnapshotStoragePlugins:
        return self._get('portfolio_snapshot_storage_plugins')

    @property
    def socket_server(self) -> SocketServer:
        return self._get('socket_server')

    @property
    def rabbit_connection(self) -> pika.BlockingConnection:
        return self._get('rabbit_connection')

    @property
    def event_emitter(self) -> EventEmitter:
        return self._get('event_emitter')

    @property
    def task_planner(self) -> TaskPlanner:
        return self._get('task_planner')

    @property
    def datetime_factory(self) -> DateTimeFactory:
        return self._get('datetime_factory')

    def create_rabbit_consumer(self, thread_watcher: ThreadWatcher) -> RabbitEventConsumer:
        connection: pika.BlockingConnection = self.create_service('rabbit_connection')
        return RabbitEventConsumer(
            thread_watcher,
            connection,
            self.socket_server,
            self.subscription_storage,
            self.candle_storage_plugins,
            self.datetime_factory
        )

    @property
    def task_consumer(self) -> TaskConsumer:
        return self._get('task_consumer')

    @property
    def strategy_replayer(self) -> StrategyReplayer:
        return self._get('strategy_replayer')

    @property
    def subscription_storage(self) -> SubscriptionStorage:
        return self._get('subscription_storage')

    @property
    def mysql_connection(self) -> MySQLdb.Connection:
        return self._get('mysql_connection')

    @property
    def strategy_run_storage(self) -> StrategyRunStorage:
        return self._get('strategy_run_storage')

    @property
    def strategy_standard_runner(self) -> StrategyStandardRunner:
        return self._get('strategy_standard_runner')
