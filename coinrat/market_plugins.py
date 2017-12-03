import pluggy
from typing import List, Set

from .plugins import PluginSpecification, plugins_loader
from .domain import Market

get_available_markets_spec = pluggy.HookspecMarker('coinrat_plugins')
get_market_spec = pluggy.HookspecMarker('coinrat_plugins')


#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class MarketPluginSpecification(PluginSpecification):
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
        self._plugins: Set[MarketPluginSpecification] = plugins_loader(
            'coinrat_market_plugins',
            MarketPluginSpecification
        )

    def get_available_markets(self) -> List[str]:
        return [market_name for plugin in self._plugins for market_name in plugin.get_available_markets()]

    def get_market(self, name: str) -> Market:
        for plugin in self._plugins:
            if name in plugin.get_available_markets():
                return plugin.get_market(name)

        raise MarketNotProvidedByAnyPluginException('Market "{}" not found.'.format(name))
