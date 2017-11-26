import os, pluggy

from influxdb import InfluxDBClient

from .candle_storage import CandleInnoDbStorage, CANDLE_STORAGE_NAME
from .order_storage import OrderInnoDbStorage, ORDER_STORAGE_NAME
from coinrat.candle_storage_plugins import CandleStoragePluginSpecification
from coinrat.order_storage_plugins import OrderStoragePluginSpecification

get_name_impl = pluggy.HookimplMarker('storage_plugins')

get_available_candle_storages_impl = pluggy.HookimplMarker('storage_plugins')
get_candle_storage_impl = pluggy.HookimplMarker('storage_plugins')

get_available_order_storages_impl = pluggy.HookimplMarker('storage_plugins')
get_order_storage_impl = pluggy.HookimplMarker('storage_plugins')

PACKAGE_NAME = 'coinrat_influx_db_storage'

influxdb_client = InfluxDBClient(
    os.environ.get('STORAGE_INFLUXFB_HOST'),
    os.environ.get('STORAGE_INFLUXFB_PORT'),
    os.environ.get('STORAGE_INFLUXFB_USER'),
    os.environ.get('STORAGE_INFLUXFB_PASSWORD'),
    os.environ.get('STORAGE_INFLUXFB_DATABASE'),
)
candle_storage = CandleInnoDbStorage(influxdb_client)
order_storage = OrderInnoDbStorage(influxdb_client)


class CandleStoragePlugin(CandleStoragePluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_candle_storages_impl
    def get_available_candle_storages(self):
        return [CANDLE_STORAGE_NAME]

    @get_candle_storage_impl
    def get_candle_storage(self, name):
        if name == CANDLE_STORAGE_NAME:
            return candle_storage

        raise ValueError('Candle storage "{}" not supported by this plugin.'.format(name))


class OrderStoragePlugin(OrderStoragePluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_order_storages_impl
    def get_available_order_storages(self):
        return [ORDER_STORAGE_NAME]

    @get_order_storage_impl
    def get_order_storage(self, name):
        if name == ORDER_STORAGE_NAME:
            return order_storage

        raise ValueError('Order storage "{}" not supported by this plugin.'.format(name))


candle_storage_plugin = CandleStoragePlugin()
order_storage_plugin = OrderStoragePlugin()
