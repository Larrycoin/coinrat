import pytest

from coinrat_influx_db_storage import storage_plugin
from coinrat_influx_db_storage.storage import MarketInnoDbStorage


def test_plugin():
    assert 'coinrat_influx_db_storage' == storage_plugin.get_name()
    assert ['influx_db'] == storage_plugin.get_available_storages()
    assert isinstance(storage_plugin.get_storage('influx_db'), MarketInnoDbStorage)
    with pytest.raises(ValueError):
        storage_plugin.get_storage('gandalf')
