import pluggy
from typing import List, Set

from .domain import Market

get_name_spec = pluggy.HookspecMarker('market_plugins')

get_available_markets_spec = pluggy.HookspecMarker('market_plugins')
get_market_spec = pluggy.HookspecMarker('market_plugins')


# Todo: solve, adding type-hints raised error:
#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class MarketPluginSpecification:
    @get_name_spec
    def get_name(self):
        pass

    @get_available_markets_spec
    def get_available_markets(self):
        pass

    @get_market_spec
    def get_market(self, name):
        pass


class MarketNotProvidedByAnyPluginException(Exception):
    pass


class MarketPlugins:
    def __init__(self) -> None:
        market_plugins = pluggy.PluginManager('market_plugins')
        market_plugins.add_hookspecs(MarketPluginSpecification)
        market_plugins.load_setuptools_entrypoints('coinrat_market_plugins')
        self._plugins: Set[MarketPluginSpecification] = market_plugins.get_plugins()

    def get_available_markets(self) -> List[str]:
        return [market_name for plugin in self._plugins for market_name in plugin.get_available_markets()]

    def get_market(self, name: str) -> Market:
        for plugin in self._plugins:
            if name in plugin.get_available_markets():
                return plugin.get_market(name)

        raise MarketNotProvidedByAnyPluginException('Market "{}" not found.'.format(name))
