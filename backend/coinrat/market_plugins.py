import pluggy
from typing import List, Set

from .domain import Market

get_name_spec = pluggy.HookspecMarker('market_plugins')

get_available_markets_spec = pluggy.HookspecMarker('market_plugins')
get_market_spec = pluggy.HookspecMarker('market_plugins')


class MarketPluginSpecification:
    @get_name_spec
    def get_name(self) -> str:
        pass

    @get_available_markets_spec
    def get_available_markets(self) -> List[str]:
        pass

    @get_market_spec
    def get_market(self, name: str) -> Market:
        pass


class MarketNotProvidedByAnyPluginException(Exception):
    pass


class MarketPlugins:
    def __init__(self):
        storage_plugins = pluggy.PluginManager('market_plugins')
        storage_plugins.add_hookspecs(MarketPluginSpecification)
        storage_plugins.load_setuptools_entrypoints('coinrat_market_plugins')
        self._plugins: Set[MarketPluginSpecification] = storage_plugins.get_plugins()

    def get_available_storages(self) -> List[str]:
        return [storage_name for plugin in self._plugins for storage_name in plugin.get_available_markets]

    def get_storage(self, name: str) -> Market:
        for plugin in self._plugins:
            if name in plugin.get_available_markets():
                return plugin.get_market(name)

        raise MarketNotProvidedByAnyPluginException('Market {} not found.'.format(name))
