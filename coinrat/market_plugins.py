import pluggy
from typing import List, Set, cast

from .plugins import PluginSpecification, plugins_loader

get_available_markets_spec = pluggy.HookspecMarker('coinrat_plugins')
get_market_spec = pluggy.HookspecMarker('coinrat_plugins')
get_market_class_spec = pluggy.HookspecMarker('coinrat_plugins')
does_support_market_spec = pluggy.HookspecMarker('coinrat_plugins')


#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class MarketPluginSpecification(PluginSpecification):
    @get_available_markets_spec
    def get_available_markets(self):
        raise NotImplementedError()

    @does_support_market_spec
    def does_support_market(self, name):
        return name in self.get_available_markets()

    @get_market_spec
    def get_market(self, name, datetime_factory, configuration):
        raise NotImplementedError()

    @get_market_class_spec
    def get_market_class(self, name):
        raise NotImplementedError()


class MarketNotProvidedByPluginException(Exception):
    pass


class MarketPluginDoesNotExistsException(Exception):
    pass


class MarketPlugins:
    def __init__(self) -> None:
        self._plugins = cast(
            Set[MarketPluginSpecification],
            plugins_loader('coinrat_market_plugins', MarketPluginSpecification)
        )

    def get_plugin(self, plugin_name: str) -> MarketPluginSpecification:
        for plugin in self._plugins:
            if plugin.get_name() == plugin_name:
                return plugin

        raise MarketPluginDoesNotExistsException('Market plugin "{}" not found.'.format(plugin_name))

    def get_available_market_plugins(self) -> List[MarketPluginSpecification]:
        return list(self._plugins)
