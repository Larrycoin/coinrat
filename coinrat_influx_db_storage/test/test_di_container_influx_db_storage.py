import pytest

from coinrat_influx_db_storage.di_container_influx_db_storage import DiContainerInfluxDbStorage


def test_influx_db_di_get_order_storage():
    container = DiContainerInfluxDbStorage()
    with pytest.raises(ValueError):
        container.get_order_storage('gandalf_the_grey')

    assert container.get_order_storage('influx_db_storage-A')._measurement_name == 'storage-A'
