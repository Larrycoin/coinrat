import pluggy
from coinrat.market_plugins import MarketPluginSpecification

from .market import MARKET_NAME, PrintDummyMarket

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_bittrex'
SYNCHRONIZER_NAME = 'bittrex'

get_available_synchronizers_spec = pluggy.HookimplMarker('synchronizer_plugins')
get_synchronizer_impl = pluggy.HookimplMarker('synchronizer_plugins')

print_dummy_market = PrintDummyMarket()


class MarketPlugin(MarketPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_markets_spec
    def get_available_markets(self):
        return [MARKET_NAME]

    @get_market_impl
    def get_market(self, name):
        if name == MARKET_NAME:
            return print_dummy_market

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))


market_plugin = MarketPlugin()
