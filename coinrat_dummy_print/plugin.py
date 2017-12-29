import pluggy
from flexmock import flexmock

from coinrat.market_plugins import MarketPluginSpecification
from coinrat.domain import DateTimeFactory
from .market import MARKET_NAME, PrintDummyMarket

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_dummy_print'

get_available_synchronizers_spec = pluggy.HookimplMarker('synchronizer_plugins')
get_synchronizer_impl = pluggy.HookimplMarker('synchronizer_plugins')


class MarketPlugin(MarketPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_markets_spec
    def get_available_markets(self):
        return [MARKET_NAME]

    @get_market_impl
    def get_market(self, name, datetime_factory, configuration):
        if name == MARKET_NAME:
            return PrintDummyMarket(datetime_factory, configuration)

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))


market_plugin = MarketPlugin()
