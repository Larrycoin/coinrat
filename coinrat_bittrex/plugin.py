import os
import pluggy
from coinrat.market_plugins import MarketPluginSpecification
from coinrat.synchronizer_plugins import SynchronizerPluginSpecification
from .synchronizer import BittrexSynchronizer

from .market import bittrex_market_factory, MARKET_NAME, BittrexMarket

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')
get_market_class_impl = pluggy.HookimplMarker('market_plugins')
get_description_impl = pluggy.HookimplMarker('market_plugins')
does_support_market_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_bittrex'
SYNCHRONIZER_NAME = 'bittrex'

bittrex_market = bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
get_available_synchronizers_spec = pluggy.HookimplMarker('synchronizer_plugins')
get_synchronizer_impl = pluggy.HookimplMarker('synchronizer_plugins')


class MarketPlugin(MarketPluginSpecification):
    @get_description_impl
    def get_description(self):
        return 'Native implementation of Bittrex using bittrex API 1.1 and 2.0.'

    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_markets_spec
    def get_available_markets(self):
        return [MARKET_NAME]

    @get_market_impl
    def get_market(self, name, datetime_factory, configuration):
        if name == MARKET_NAME:
            return bittrex_market

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))

    @get_market_class_impl
    def get_market_class(self, name):
        if name == MARKET_NAME:
            return BittrexMarket

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
    def get_synchronizer(self, synchronizer_name, storage, event_emitter):
        if synchronizer_name == SYNCHRONIZER_NAME:
            return BittrexSynchronizer(bittrex_market, storage, event_emitter)

        raise ValueError('Synchronizer "{}" not supported by this plugin.'.format(synchronizer_name))


synchronizer_plugin = SynchronizerPlugin()
