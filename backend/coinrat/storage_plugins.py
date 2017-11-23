import pluggy
from typing import List, Set

from .domain import MarketsCandleStorage

get_name_spec = pluggy.HookspecMarker('storage_plugins')

get_available_storages_spec = pluggy.HookspecMarker('storage_plugins')
get_storage_spec = pluggy.HookspecMarker('storage_plugins')


# Todo: solve, adding type-hints raised error:
#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class StoragePluginSpecification:
    @get_name_spec
    def get_name(self):
        pass

    @get_available_storages_spec
    def get_available_storages(self):
        pass

    @get_storage_spec
    def get_storage(self, name):
        pass


class StorageNotProvidedByAnyPluginException(Exception):
    pass


class StoragePlugins:
    def __init__(self):
        storage_plugins = pluggy.PluginManager('storage_plugins')
        storage_plugins.add_hookspecs(StoragePluginSpecification)
        storage_plugins.load_setuptools_entrypoints('coinrat_storage_plugins')
        self._plugins: Set[StoragePluginSpecification] = storage_plugins.get_plugins()

    def get_available_storages(self) -> List[str]:
        return [storage_name for plugin in self._plugins for storage_name in plugin.get_available_storages]

    def get_storage(self, name: str) -> MarketsCandleStorage:
        for plugin in self._plugins:
            if name in plugin.get_available_storages():
                return plugin.get_storage(name)

        raise StorageNotProvidedByAnyPluginException('Storage "{}" not found.'.format(name))
