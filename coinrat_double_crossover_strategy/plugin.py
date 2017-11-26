import datetime
import pluggy

from coinrat.strategy_plugins import StrategyPluginSpecification
from coinrat.domain import Pair

from .strategy import DoubleCrossoverStrategy, STRATEGY_NAME

get_name_impl = pluggy.HookimplMarker('strategy_plugins')
get_available_strategies_spec = pluggy.HookimplMarker('strategy_plugins')
get_strategy_impl = pluggy.HookimplMarker('strategy_plugins')

PACKAGE_NAME = 'coinrat_double_crossover_strategy'


class StrategyPlugin(StrategyPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_strategies_spec
    def get_available_strategies(self):
        return [STRATEGY_NAME]

    @get_strategy_impl
    def get_strategy(self, name, candle_storage, order_storage):
        if name == STRATEGY_NAME:
            return DoubleCrossoverStrategy(
                Pair('USD', 'BTC'),  # Todo: make this parameter for end user
                candle_storage,
                order_storage,
                datetime.timedelta(hours=1),
                datetime.timedelta(minutes=15)
            )

        raise ValueError('Strategy "{}" not supported by this plugin.'.format(name))


strategy_plugin = StrategyPlugin()
