import pluggy

from coinrat.portfolio_snapshot_storage_plugins import PortfolioSnapshotStoragePluginSpecification
from coinrat_influx_db_storage.portfolio_snapshot_storage import PORTFOLIO_SNAPSHOT_STORAGE_NAME
from .di_container_influx_db_storage import DiContainerInfluxDbStorage
from .candle_storage import CANDLE_STORAGE_NAME
from .order_storage import ORDER_STORAGE_NAME, MEASUREMENT_ORDERS_NAMES
from coinrat.candle_storage_plugins import CandleStoragePluginSpecification
from coinrat.order_storage_plugins import OrderStoragePluginSpecification

get_name_impl = pluggy.HookimplMarker('storage_plugins')

get_available_candle_storages_impl = pluggy.HookimplMarker('storage_plugins')
get_candle_storage_impl = pluggy.HookimplMarker('storage_plugins')

get_available_order_storages_impl = pluggy.HookimplMarker('storage_plugins')
get_order_storage_impl = pluggy.HookimplMarker('storage_plugins')

get_available_portfolio_snapshot_storages_impl = pluggy.HookimplMarker('storage_plugins')
get_portfolio_snapshot_storage_impl = pluggy.HookimplMarker('storage_plugins')

PACKAGE_NAME = 'coinrat_influx_db_storage'

di_container = DiContainerInfluxDbStorage()


class CandleStoragePlugin(CandleStoragePluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_candle_storages_impl
    def get_available_candle_storages(self):
        return [CANDLE_STORAGE_NAME]

    @get_candle_storage_impl
    def get_candle_storage(self, name):
        return di_container.get_candle_storage(name)


class OrderStoragePlugin(OrderStoragePluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_order_storages_impl
    def get_available_order_storages(self):
        return list(map(
            lambda measurement_name: '{}_{}'.format(ORDER_STORAGE_NAME, measurement_name),
            MEASUREMENT_ORDERS_NAMES
        ))

    @get_order_storage_impl
    def get_order_storage(self, name):
        return di_container.get_order_storage(name)


class PorfolioSnapshotStoragePlugin(PortfolioSnapshotStoragePluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_portfolio_snapshot_storages_impl
    def get_available_portfolio_snapshot_storages(self):
        return [PORTFOLIO_SNAPSHOT_STORAGE_NAME]

    @get_portfolio_snapshot_storage_impl
    def get_portfolio_snapshot_storage(self, name):
        return di_container.get_portfolio_snapshot_storage(name)


candle_storage_plugin = CandleStoragePlugin()
order_storage_plugin = OrderStoragePlugin()
portfolio_snapshot_storage_plugin = PorfolioSnapshotStoragePlugin()
