import os
import pluggy
from coinrat.market_plugins import MarketPluginSpecification
from coinrat.synchronizer_plugins import SynchronizerPluginSpecification
from .synchronizer import BittrexSynchronizer

from .market import bittrex_market_factory

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_bittrex'
MARKET_NAME = 'bittrex'
SYNCHRONIZER_NAME = 'bittrex'

bittrex_market = bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
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
    def get_market(self, name):
        if name == MARKET_NAME:
            return bittrex_market

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))


market_plugin = MarketPlugin()


class SynchronizerPlugin(SynchronizerPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_synchronizers_spec
    def get_available_synchronizers(self):
        return [SYNCHRONIZER_NAME]

    @get_synchronizer_impl
    def get_synchronizer(self, name, storage):
        if name == SYNCHRONIZER_NAME:
            return BittrexSynchronizer(
                bittrex_market,
                storage
                # Todo: make possible to parametrize synchronizer
            )

        raise ValueError('Synchronizer "{}" not supported by this plugin.'.format(name))


synchronizer_plugin = SynchronizerPlugin()
