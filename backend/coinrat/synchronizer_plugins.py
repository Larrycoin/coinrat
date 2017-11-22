import pluggy
from typing import List, Set

from .domain import MarketStateSynchronizer, MarketsCandleStorage

get_name_spec = pluggy.HookspecMarker('synchronizer_plugins')

get_available_synchronizers_spec = pluggy.HookspecMarker('synchronizer_plugins')
get_synchronizer_spec = pluggy.HookspecMarker('synchronizer_plugins')


class SynchronizerPluginSpecification:
    @get_name_spec
    def get_name(self):
        pass

    @get_available_synchronizers_spec
    def get_available_synchronizers(self):
        pass

    @get_synchronizer_spec
    def get_synchronizer(self, name, storage):
        pass


class SynchronizerNotProvidedByAnyPluginException(Exception):
    pass


class SynchronizerPlugins:
    def __init__(self):
        storage_plugins = pluggy.PluginManager('synchronizer_plugins')
        storage_plugins.add_hookspecs(SynchronizerPluginSpecification)
        storage_plugins.load_setuptools_entrypoints('coinrat_synchronizer_plugins')
        self._plugins: Set[SynchronizerPluginSpecification] = storage_plugins.get_plugins()
        print(self._plugins)

    def get_available_synchronizers(self) -> List[str]:
        return [synchronize_name for plugin in self._plugins for synchronize_name in plugin.get_available_synchronizers]

    def get_synchronizer(self, name: str, storage: MarketsCandleStorage) -> MarketStateSynchronizer:
        for plugin in self._plugins:
            if name in plugin.get_available_synchronizers():
                return plugin.get_synchronizer(name, storage)

        raise SynchronizerNotProvidedByAnyPluginException('Synchronizer "{}" not found.'.format(name))
