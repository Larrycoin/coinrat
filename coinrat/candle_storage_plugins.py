import pluggy
from typing import List, Set

from .plugins import PluginSpecification, plugins_loader
from .domain.candle import CandleStorage

get_available_candle_storages_spec = pluggy.HookspecMarker('coinrat_plugins')
get_candle_storage_spec = pluggy.HookspecMarker('coinrat_plugins')


#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class CandleStoragePluginSpecification(PluginSpecification):
    @get_available_candle_storages_spec
    def get_available_candle_storages(self):
        pass

    @get_candle_storage_spec
    def get_candle_storage(self, name):
        pass


class CandleStorageNotProvidedByAnyPluginException(Exception):
    pass


class CandleStoragePlugins:
    def __init__(self) -> None:
        self._plugins: Set[CandleStoragePluginSpecification] = plugins_loader(
            'coinrat_candle_storage_plugins',
            CandleStoragePluginSpecification
        )

    def get_available_candle_storages(self) -> List[str]:
        return [storage_name for plugin in self._plugins for storage_name in plugin.get_available_candle_storages()]

    def get_candle_storage(self, name: str) -> CandleStorage:
        for plugin in self._plugins:
            if name in plugin.get_available_candle_storages():
                return plugin.get_candle_storage(name)

        raise CandleStorageNotProvidedByAnyPluginException('Candle storage "{}" not found.'.format(name))
