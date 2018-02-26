import pytest

from coinrat_influx_db_storage import candle_storage_plugin, order_storage_plugin, portfolio_snapshot_storage_plugin
from coinrat_influx_db_storage.candle_storage import CandleInnoDbStorage
from coinrat_influx_db_storage.order_storage import OrderInnoDbStorage
from coinrat_influx_db_storage.portfolio_snapshot_storage import PortfolioSnapshotStorage


def test_candle_plugin():
    assert 'coinrat_influx_db_storage' == candle_storage_plugin.get_name()
    assert ['influx_db'] == candle_storage_plugin.get_available_candle_storages()
    assert isinstance(candle_storage_plugin.get_candle_storage('influx_db'), CandleInnoDbStorage)
    with pytest.raises(ValueError):
        candle_storage_plugin.get_candle_storage('gandalf')


def test_order_plugin():
    assert 'coinrat_influx_db_storage' == order_storage_plugin.get_name()
    assert order_storage_plugin.get_available_order_storages() == [
        'influx_db_orders-A',
        'influx_db_orders-B',
        'influx_db_orders-C',
        'influx_db_orders-D',
        'influx_db_orders-E',
    ]
    assert isinstance(order_storage_plugin.get_order_storage('influx_db'), OrderInnoDbStorage)
    with pytest.raises(ValueError):
        order_storage_plugin.get_order_storage('gandalf')


def test_portfolio_snapshot_plugin():
    assert 'coinrat_influx_db_storage' == portfolio_snapshot_storage_plugin.get_name()
    assert ['influx_db'] == portfolio_snapshot_storage_plugin.get_available_portfolio_snapshot_storages()
    assert isinstance(
        portfolio_snapshot_storage_plugin.get_portfolio_snapshot_storage('influx_db'),
        PortfolioSnapshotStorage
    )
    with pytest.raises(ValueError):
        portfolio_snapshot_storage_plugin.get_portfolio_snapshot_storage('gandalf')
