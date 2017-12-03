import pytest

from coinrat_memory_storage import candle_storage_plugin, order_storage_plugin
from coinrat_memory_storage.candle_storage import CandleMemoryStorage
from coinrat_memory_storage.order_storage import OrderMemoryStorage


def test_candle_plugin():
    assert 'coinrat_memory_storage' == candle_storage_plugin.get_name()
    assert ['memory'] == candle_storage_plugin.get_available_candle_storages()
    assert isinstance(candle_storage_plugin.get_candle_storage('memory'), CandleMemoryStorage)
    with pytest.raises(ValueError):
        candle_storage_plugin.get_candle_storage('gandalf')


def test_order_plugin():
    assert 'coinrat_memory_storage' == order_storage_plugin.get_name()
    assert ['memory'] == order_storage_plugin.get_available_order_storages()
    assert isinstance(order_storage_plugin.get_order_storage('memory'), OrderMemoryStorage)
    with pytest.raises(ValueError):
        order_storage_plugin.get_order_storage('gandalf')
