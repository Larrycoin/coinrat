import logging

import ccxt
import pluggy
from coinrat.market_plugins import MarketPluginSpecification
from coinrat.synchronizer_plugins import SynchronizerPluginSpecification
from coinrat_cctx.synchronizer import CctxSynchronizer

from .market import MARKET_NAME, CctxMarket

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')
get_market_class_impl = pluggy.HookimplMarker('market_plugins')
get_description_impl = pluggy.HookimplMarker('market_plugins')
does_support_market_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_cctx'

SYNCHRONIZER_NAME = 'cctx'
get_available_synchronizers_spec = pluggy.HookimplMarker('synchronizer_plugins')
get_synchronizer_impl = pluggy.HookimplMarker('synchronizer_plugins')

logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)


class MarketPlugin(MarketPluginSpecification):
    @get_description_impl
    def get_description(self):
        return 'All markets supported by CCTX library are available via this module.'

    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_markets_spec
    def get_available_markets(self):
        return ccxt.exchanges

    @get_market_impl
    def get_market(self, name, datetime_factory, configuration):
        if name in self.get_available_markets():
            return CctxMarket(name)

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))

    @get_market_class_impl
    def get_market_class(self, name):
        if name == MARKET_NAME:
            return CctxMarket

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
            return CctxSynchronizer(bittrex_market, storage, event_emitter)

        raise ValueError('Synchronizer "{}" not supported by this plugin.'.format(synchronizer_name))


synchronizer_plugin = SynchronizerPlugin()
