import pytest
from flexmock import flexmock

from coinrat.market_plugins import MarketPlugins, MarketNotProvidedByAnyPluginException
from coinrat.candle_storage_plugins import CandleStoragePlugins, CandleStorageNotProvidedByAnyPluginException
from coinrat.strategy_plugins import StrategyPlugins, StrategyNotProvidedByAnyPluginException
from coinrat.synchronizer_plugins import SynchronizerPlugins, SynchronizerNotProvidedByAnyPluginException
from coinrat.domain import MarketsCandleStorage, Strategy, Market, MarketStateSynchronizer


def test_synchronizer_plugins():
    plugins = SynchronizerPlugins()
    assert 'bittrex' in plugins.get_available_synchronizers()
    assert 'cryptocompare' in plugins.get_available_synchronizers()

    assert isinstance(plugins.get_synchronizer('cryptocompare', flexmock()), MarketStateSynchronizer)
    with pytest.raises(SynchronizerNotProvidedByAnyPluginException):
        plugins.get_synchronizer('gandalf', flexmock())


def test_market_plugins():
    plugins = MarketPlugins()
    assert 'bittrex' in plugins.get_available_markets()
    assert 'dummy_print' in plugins.get_available_markets()

    assert isinstance(plugins.get_market('bittrex'), Market)
    with pytest.raises(MarketNotProvidedByAnyPluginException):
        plugins.get_market('gandalf')


def test_candle_storage_plugins():
    plugins = CandleStoragePlugins()
    assert 'influx_db' in plugins.get_available_candle_storages()

    assert isinstance(plugins.get_candle_storage('influx_db'), MarketsCandleStorage)
    with pytest.raises(CandleStorageNotProvidedByAnyPluginException):
        plugins.get_candle_storage('gandalf')


def test_strategy_plugins():
    plugins = StrategyPlugins()
    assert 'double_crossover' in plugins.get_available_strategies()

    assert isinstance(plugins.get_strategy('double_crossover', flexmock()), Strategy)
    with pytest.raises(StrategyNotProvidedByAnyPluginException):
        plugins.get_strategy('gandalf', flexmock())
