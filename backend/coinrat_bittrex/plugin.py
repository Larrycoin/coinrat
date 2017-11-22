import os
import pluggy
from coinrat.market_plugins import MarketPluginSpecification
from .market import bittrex_market_factory, MARKET_BITREX

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')


class MarketPlugin(MarketPluginSpecification):
    @get_name_impl
    def get_name(self):
        return 'bittrex'

    @get_available_markets_spec
    def get_available_markets(self):
        return ['bittrex']

    @get_market_impl
    def get_market(self, name):
        if name == MARKET_BITREX:
            return bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))


market_plugin = MarketPlugin()
