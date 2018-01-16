import pluggy

from coinrat.strategy_plugins import StrategyPluginSpecification
from .strategy import DoubleCrossoverStrategy, STRATEGY_NAME

get_name_impl = pluggy.HookimplMarker('strategy_plugins')
get_available_strategies_spec = pluggy.HookimplMarker('strategy_plugins')
get_strategy_impl = pluggy.HookimplMarker('strategy_plugins')
get_strategy_class_impl = pluggy.HookimplMarker('strategy_plugins')

PACKAGE_NAME = 'coinrat_double_crossover_strategy'


class StrategyPlugin(StrategyPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_strategies_spec
    def get_available_strategies(self):
        return [STRATEGY_NAME]

    @get_strategy_impl
    def get_strategy(self, name, candle_storage, order_storage, event_emitter, datetime_factory, configuration):
        if name == STRATEGY_NAME:
            return DoubleCrossoverStrategy(
                candle_storage,
                order_storage,
                event_emitter,
                datetime_factory,
                configuration
            )

        raise ValueError('Strategy "{}" not supported by this plugin.'.format(name))

    @get_strategy_class_impl
    def get_strategy_class(self, name):
        if name == STRATEGY_NAME:
            return DoubleCrossoverStrategy

        raise ValueError('Strategy "{}" not supported by this plugin.'.format(name))


strategy_plugin = StrategyPlugin()
