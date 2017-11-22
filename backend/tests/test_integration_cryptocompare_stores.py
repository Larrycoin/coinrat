
import pytest
import requests
from influxdb import InfluxDBClient

from coinrat_cryptocompare import CryptocompareSynchronizer
from coinrat_influx_db_storage import MarketInnoDbStorage
from coinrat.domain import MarketPair


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


def test_candle_ticks_are_stored(influx_database: InfluxDBClient):
    synchronizer = CryptocompareSynchronizer(
        'bittrex',
        MarketInnoDbStorage(influx_database),
        requests.Session(),
        delay=0,
        number_of_runs=1
    )
    synchronizer.synchronize(MarketPair('USD', 'BTC'))

    stored_candles = _get_all_from_influx_db(influx_database)
    assert 2 == len(stored_candles)

    # Test that same data won't be stored twice
    synchronizer.synchronize(MarketPair('USD', 'BTC'))
    second_sample = _get_all_from_influx_db(influx_database)
    assert stored_candles == second_sample


def _get_all_from_influx_db(influx_database: InfluxDBClient):
    return list(influx_database.query('SELECT * FROM candles').get_points())
