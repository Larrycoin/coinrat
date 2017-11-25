import pluggy
from typing import List

from .plugins import PluginSpecification, plugins_loader
from .domain import MarketsCandleStorage

get_available_storages_spec = pluggy.HookspecMarker('coinrat_plugins')
get_storage_spec = pluggy.HookspecMarker('coinrat_plugins')


# Todo: solve, adding type-hints raised error:
#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class StoragePluginSpecification(PluginSpecification):
    @get_available_storages_spec
    def get_available_storages(self):
        pass

    @get_storage_spec
    def get_storage(self, name):
        pass


class StorageNotProvidedByAnyPluginException(Exception):
    pass


class StoragePlugins:
    def __init__(self) -> None:
        self._plugins = plugins_loader('coinrat_storage_plugins', StoragePluginSpecification)

    def get_available_storages(self) -> List[str]:
        return [storage_name for plugin in self._plugins for storage_name in plugin.get_available_storages()]

    def get_storage(self, name: str) -> MarketsCandleStorage:
        for plugin in self._plugins:
            if name in plugin.get_available_storages():
                return plugin.get_storage(name)

        raise StorageNotProvidedByAnyPluginException('Storage "{}" not found.'.format(name))
