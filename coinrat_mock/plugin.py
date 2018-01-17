import pluggy
from flexmock import flexmock

from coinrat.market_plugins import MarketPluginSpecification
from coinrat.domain import DateTimeFactory
from .market import MARKET_NAME, MockMarket

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')
get_market_class_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_mock'


class MarketPlugin(MarketPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_markets_spec
    def get_available_markets(self):
        return [MARKET_NAME]

    @get_market_impl
    def get_market(self, name, datetime_factory, configuration):
        return MockMarket(datetime_factory, configuration)

    @get_market_class_impl
    def get_market_class(self, name):
        if name == MARKET_NAME:
            return MockMarket

        raise ValueError('Market "{}" not supported by this plugin.'.format(name))


market_plugin = MarketPlugin()
