import pluggy
from typing import List, Set, cast

from coinrat.domain import DateTimeFactory
from coinrat.domain.order import OrderStorage
from coinrat.domain.strategy import Strategy, StrategyRun
from coinrat.event.event_emitter import EventEmitter
from .plugins import PluginSpecification, plugins_loader
from .domain.candle import CandleStorage

get_available_strategies_spec = pluggy.HookspecMarker('coinrat_plugins')
get_strategy_spec = pluggy.HookspecMarker('coinrat_plugins')
get_strategy_class_spec = pluggy.HookspecMarker('coinrat_plugins')


#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class StrategyPluginSpecification(PluginSpecification):
    @get_available_strategies_spec
    def get_available_strategies(self):
        raise NotImplementedError()

    @get_strategy_spec
    def get_strategy(self, name, candle_storage, order_storage, event_emitter, datetime_factory, strategy_run):
        raise NotImplementedError()

    @get_strategy_class_spec
    def get_strategy_class(self, name):
        raise NotImplementedError()


class StrategyNotProvidedByAnyPluginException(Exception):
    pass


class StrategyPlugins:
    def __init__(self) -> None:
        self._plugins = cast(
            Set[StrategyPluginSpecification],
            plugins_loader('coinrat_strategy_plugins', StrategyPluginSpecification)
        )

    def get_available_strategies(self) -> List[str]:
        return [strategy_name for plugin in self._plugins for strategy_name in plugin.get_available_strategies()]

    def get_strategy_class(self, name: str):
        for plugin in self._plugins:
            if name in plugin.get_available_strategies():
                return plugin.get_strategy_class(name)

        raise StrategyNotProvidedByAnyPluginException('Strategy "{}" not found.'.format(name))

    def get_strategy(
        self,
        name: str,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        event_emitter: EventEmitter,
        datetime_factory: DateTimeFactory,
        strategy_run: StrategyRun
    ) -> Strategy:
        for plugin in self._plugins:
            if name in plugin.get_available_strategies():
                return plugin.get_strategy(
                    name,
                    candle_storage,
                    order_storage,
                    event_emitter,
                    datetime_factory,
                    strategy_run
                )

        raise StrategyNotProvidedByAnyPluginException('Strategy "{}" not found.'.format(name))
