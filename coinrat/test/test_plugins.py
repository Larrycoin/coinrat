import pytest
from flexmock import flexmock

from coinrat.domain import MarketStateSynchronizer
from coinrat.domain.market import Market
from coinrat.domain.order import OrderStorage
from coinrat.domain.candle import CandleStorage
from coinrat.domain.strategy import Strategy
from coinrat.market_plugins import MarketPlugins, MarketNotProvidedByAnyPluginException
from coinrat.candle_storage_plugins import CandleStoragePlugins, CandleStorageNotProvidedByAnyPluginException
from coinrat.strategy_plugins import StrategyPlugins, StrategyNotProvidedByAnyPluginException
from coinrat.synchronizer_plugins import SynchronizerPlugins, SynchronizerNotProvidedByAnyPluginException
from coinrat.order_storage_plugins import OrderStoragePlugins, OrderStorageNotProvidedByAnyPluginException


def test_synchronizer_plugins():
    plugins = SynchronizerPlugins()
    assert 'bittrex' in plugins.get_available_synchronizers()
    assert 'cryptocompare' in plugins.get_available_synchronizers()

    assert isinstance(plugins.get_synchronizer('cryptocompare', flexmock(), flexmock()), MarketStateSynchronizer)
    with pytest.raises(SynchronizerNotProvidedByAnyPluginException):
        plugins.get_synchronizer('gandalf', flexmock(), flexmock())


def test_market_plugins():
    plugins = MarketPlugins()
    assert 'bittrex' in plugins.get_available_markets()
    assert 'mock' in plugins.get_available_markets()

    assert isinstance(plugins.get_market('bittrex', flexmock(), {}), Market)
    with pytest.raises(MarketNotProvidedByAnyPluginException):
        plugins.get_market('gandalf', flexmock(), {})


def test_candle_storage_plugins():
    plugins = CandleStoragePlugins()
    assert 'influx_db' in plugins.get_available_candle_storages()

    assert isinstance(plugins.get_candle_storage('influx_db'), CandleStorage)
    with pytest.raises(CandleStorageNotProvidedByAnyPluginException):
        plugins.get_candle_storage('gandalf')


def test_order_storage_plugins():
    plugins = OrderStoragePlugins()
    assert 'influx_db_orders-A' in plugins.get_available_order_storages()

    assert isinstance(plugins.get_order_storage('influx_db_orders-A'), OrderStorage)
    with pytest.raises(OrderStorageNotProvidedByAnyPluginException):
        plugins.get_order_storage('gandalf')


def test_strategy_plugins():
    plugins = StrategyPlugins()
    assert 'double_crossover' in plugins.get_available_strategies()

    strategy_run_mock = flexmock(strategy_configuration={})

    assert isinstance(
        plugins.get_strategy('double_crossover', flexmock(), flexmock(), flexmock(), flexmock(), strategy_run_mock),
        Strategy
    )
    with pytest.raises(StrategyNotProvidedByAnyPluginException):
        plugins.get_strategy('gandalf', flexmock(), flexmock(), flexmock(), flexmock(), strategy_run_mock)
