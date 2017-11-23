import pluggy

from coinrat.storage_plugins import StoragePluginSpecification
from .storage import market_storage_factory, STORAGE_NAME

get_name_impl = pluggy.HookimplMarker('storage_plugins')
get_available_storages_spec = pluggy.HookimplMarker('storage_plugins')
get_storage_impl = pluggy.HookimplMarker('storage_plugins')

PACKAGE_NAME = 'coinrat_influx_db_storage'

storage = market_storage_factory('coinrat')  # Todo: move to .env


class StoragePlugin(StoragePluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_storages_spec
    def get_available_storages(self):
        return [STORAGE_NAME]

    @get_storage_impl
    def get_storage(self, name):
        if name == STORAGE_NAME:
            return storage

        raise ValueError('Storage "{}" not supported by this plugin.'.format(name))


storage_plugin = StoragePlugin()
