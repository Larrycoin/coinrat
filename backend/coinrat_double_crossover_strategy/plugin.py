import datetime
import pluggy

from coinrat.strategy_plugins import StrategyPluginSpecification
from coinrat.domain import MarketPair

from .strategy import DoubleCrossoverStrategy

get_name_impl = pluggy.HookimplMarker('strategy_plugins')
get_available_strategies_spec = pluggy.HookimplMarker('strategy_plugins')
get_strategy_impl = pluggy.HookimplMarker('strategy_plugins')

PACKAGE_NAME = 'coinrat_double_crossover_strategy'
STRATEGY_NAME = 'double_crossover'


class StrategyPlugin(StrategyPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_strategies_spec
    def get_available_strategies(self):
        return [STRATEGY_NAME]

    @get_strategy_impl
    def get_strategy(self, name, storage):
        if name == STRATEGY_NAME:
            return DoubleCrossoverStrategy(
                MarketPair('USD', 'BTC'),  # Todo: make this parameter for end user
                storage,
                datetime.timedelta(hours=1),
                datetime.timedelta(minutes=15)
            )

        raise ValueError('Strategy "{}" not supported by this plugin.'.format(name))


strategy_plugin = StrategyPlugin()
