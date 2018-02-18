from typing import List

import pluggy
from coinrat.market_plugins import MarketPluginSpecification
from .market import MockMarket

get_name_impl = pluggy.HookimplMarker('market_plugins')
get_description_impl = pluggy.HookimplMarker('market_plugins')
get_available_markets_spec = pluggy.HookimplMarker('market_plugins')
get_market_impl = pluggy.HookimplMarker('market_plugins')
get_market_class_impl = pluggy.HookimplMarker('market_plugins')
does_support_market_impl = pluggy.HookimplMarker('market_plugins')

PLUGIN_NAME = 'coinrat_mock'


class MarketPlugin(MarketPluginSpecification):
    def __init__(self):
        self._available_markets_names = []

    @get_description_impl
    def get_description(self):
        return 'Plugin mocks any market.'

    @get_name_impl
    def get_name(self):
        return PLUGIN_NAME

    @get_available_markets_spec
    def get_available_markets(self):
        return self._available_markets_names

    def set_available_markets(self, available_markets_names: List[str]) -> None:
        self._available_markets_names = available_markets_names

    @does_support_market_impl
    def does_support_market(self, name):
        return True

    @get_market_impl
    def get_market(self, name, datetime_factory, configuration):
        if 'mocked_market_name' not in configuration:
            configuration['mocked_market_name'] = name

        if configuration['mocked_market_name'] != name:
            raise ValueError('Configuration "{}" does not match "{}"')

        return MockMarket(datetime_factory, configuration)

    @get_market_class_impl
    def get_market_class(self, name):
        return MockMarket


market_plugin = MarketPlugin()
