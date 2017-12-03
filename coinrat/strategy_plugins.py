import pluggy
from typing import List, Set

from .plugins import PluginSpecification, plugins_loader
from .domain import Strategy
from .domain.candle import CandleStorage
from coinrat.domain.order import OrderStorage

get_available_strategies_spec = pluggy.HookspecMarker('coinrat_plugins')
get_strategy_spec = pluggy.HookspecMarker('coinrat_plugins')


# Todo: solve, adding type-hints raises error:
#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class StrategyPluginSpecification(PluginSpecification):
    @get_available_strategies_spec
    def get_available_strategies(self):
        pass

    @get_strategy_spec
    def get_strategy(self, name, candle_storage, order_storage):
        pass


class StrategyNotProvidedByAnyPluginException(Exception):
    pass


class StrategyPlugins:
    def __init__(self) -> None:
        self._plugins: Set[StrategyPluginSpecification] = plugins_loader(
            'coinrat_strategy_plugins',
            StrategyPluginSpecification
        )

    def get_available_strategies(self) -> List[str]:
        return [strategy_name for plugin in self._plugins for strategy_name in plugin.get_available_strategies()]

    def get_strategy(
        self,
        name: str,
        candle_storage: CandleStorage,
        order_storage: OrderStorage
    ) -> Strategy:
        for plugin in self._plugins:
            if name in plugin.get_available_strategies():
                return plugin.get_strategy(name, candle_storage, order_storage)

        raise StrategyNotProvidedByAnyPluginException('Strategy "{}" not found.'.format(name))
