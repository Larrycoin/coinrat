import pluggy
from typing import List, Set

from .domain import Strategy, MarketsCandleStorage

get_name_spec = pluggy.HookspecMarker('strategy_plugins')

get_available_strategies_spec = pluggy.HookspecMarker('strategy_plugins')
get_strategy_spec = pluggy.HookspecMarker('strategy_plugins')


# Todo: solve, adding type-hints raised error:
#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class StrategyPluginSpecification:
    @get_name_spec
    def get_name(self):
        pass

    @get_available_strategies_spec
    def get_available_strategies(self):
        pass

    @get_strategy_spec
    def get_strategy(self, name, storage):
        pass


class StrategyNotProvidedByAnyPluginException(Exception):
    pass


class StrategyPlugins:
    def __init__(self) -> None:
        strategy_plugins = pluggy.PluginManager('strategy_plugins')
        strategy_plugins.add_hookspecs(StrategyPluginSpecification)
        strategy_plugins.load_setuptools_entrypoints('coinrat_strategy_plugins')
        self._plugins: Set[StrategyPluginSpecification] = strategy_plugins.get_plugins()

    def get_available_strategies(self) -> List[str]:
        return [strategy_name for plugin in self._plugins for strategy_name in plugin.get_available_strategies]

    def get_strategy(self, name: str, storage: MarketsCandleStorage) -> Strategy:
        for plugin in self._plugins:
            if name in plugin.get_available_strategies():
                return plugin.get_strategy(name, storage)

        raise StrategyNotProvidedByAnyPluginException('Strategy "{}" not found.'.format(name))
