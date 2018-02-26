import pytest
from flexmock import flexmock

from coinrat.domain import MarketStateSynchronizer
from coinrat.domain.order import OrderStorage
from coinrat.domain.candle import CandleStorage
from coinrat.domain.portfolio import PortfolioSnapshotStorage
from coinrat.domain.strategy import Strategy
from coinrat.market_plugins import MarketPlugins, MarketPluginSpecification, MarketPluginDoesNotExistsException
from coinrat.candle_storage_plugins import CandleStoragePlugins, CandleStorageNotProvidedByAnyPluginException
from coinrat.portfolio_snapshot_storage_plugins import PortfolioSnapshotStoragePlugins, \
    PortfolioSnapshotStorageNotProvidedByAnyPluginException
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

    mock_plugin = plugins.get_plugin('coinrat_mock')
    assert isinstance(mock_plugin, MarketPluginSpecification)
    bittrex_plugin = plugins.get_plugin('coinrat_bittrex')
    assert isinstance(bittrex_plugin, MarketPluginSpecification)

    with pytest.raises(MarketPluginDoesNotExistsException):
        plugins.get_plugin('gandalf')


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
        plugins.get_strategy('double_crossover', flexmock(), flexmock(), flexmock(), strategy_run_mock),
        Strategy
    )
    with pytest.raises(StrategyNotProvidedByAnyPluginException):
        plugins.get_strategy('gandalf', flexmock(), flexmock(), flexmock(), strategy_run_mock)


def test_portfolio_snapshot_storage_plugins():
    plugins = PortfolioSnapshotStoragePlugins()
    assert 'influx_db' in plugins.get_available_portfolio_snapshot_storages()

    assert isinstance(plugins.get_portfolio_snapshot_storage('influx_db'), PortfolioSnapshotStorage)
    with pytest.raises(PortfolioSnapshotStorageNotProvidedByAnyPluginException):
        plugins.get_portfolio_snapshot_storage('gandalf')
