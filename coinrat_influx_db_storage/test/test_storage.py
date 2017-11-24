from typing import Tuple

import pytest, datetime
from flexmock import flexmock
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import MinuteCandle, MarketPair, CANDLE_STORAGE_FIELD_CLOSE, NoCandlesForMarketInStorageException
from coinrat_influx_db_storage.storage import MarketInnoDbStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = MarketPair('USD', 'BTC')


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


def test_write_candle(influx_database: InfluxDBClient):
    storage = MarketInnoDbStorage(influx_database)

    storage.write_candle(_create_dummy_candle())

    data = _get_all_from_influx_db(influx_database)
    assert 1 == len(data)
    expected_data = "{" \
                    + "'time': '2017-07-02T00:00:00Z', " \
                    + "'close': 8300, " \
                    + "'high': 8100, " \
                    + "'low': 8200, " \
                    + "'market': 'dummy_market', " \
                    + "'open': 8000, " \
                    + "'pair': 'USD_BTC'" \
                    + "}"
    assert expected_data == str(data[0])


def test_write_candles(influx_database: InfluxDBClient):
    storage = MarketInnoDbStorage(influx_database)

    storage.write_candles([_create_dummy_candle(1), _create_dummy_candle(2)])

    data = _get_all_from_influx_db(influx_database)
    assert 2 == len(data)
    assert '2017-07-02T00:01:00Z' == data[0]['time']
    assert '2017-07-02T00:02:00Z' == data[1]['time']


def test_write_zero_candles():
    mock_influx_database = flexmock()
    mock_influx_database.should_receive('write_points').never()

    storage = MarketInnoDbStorage(mock_influx_database)
    storage.write_candles([])


@pytest.mark.parametrize(['expected_mean', 'minute_interval'],
    [
        (8000, (0, 15)),
        (8300, (15, 30)),
        (8150, (0, 30)),
    ]
)
def test_mean(influx_database: InfluxDBClient, expected_mean: int, minute_interval: Tuple[int, int]):
    storage = MarketInnoDbStorage(influx_database)
    storage.write_candles([_create_dummy_candle(10, 8000), _create_dummy_candle(20, 8300)])
    interval = (
        datetime.datetime(2017, 7, 2, 0, minute_interval[0], 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2017, 7, 2, 0, minute_interval[1], 0, tzinfo=datetime.timezone.utc)
    )
    mean = storage.mean(DUMMY_MARKET, BTC_USD_PAIR, CANDLE_STORAGE_FIELD_CLOSE, interval)

    assert Decimal(expected_mean) == mean


def test_mean_no_data_raise_exception(influx_database: InfluxDBClient):
    """We want to raise exception to prevent invalid signal by dropping some price to 0."""
    storage = MarketInnoDbStorage(influx_database)
    interval = (
        datetime.datetime(2017, 7, 2, 0, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2017, 7, 2, 0, 30, 0, tzinfo=datetime.timezone.utc)
    )
    with pytest.raises(NoCandlesForMarketInStorageException):
        storage.mean(DUMMY_MARKET, BTC_USD_PAIR, CANDLE_STORAGE_FIELD_CLOSE, interval)


def _create_dummy_candle(minute: int = 0, close: int = 8300) -> MinuteCandle:
    return MinuteCandle(
        DUMMY_MARKET,
        BTC_USD_PAIR,
        datetime.datetime(2017, 7, 2, 0, minute, 0, tzinfo=datetime.timezone.utc),
        Decimal(8000),
        Decimal(8100),
        Decimal(8200),
        Decimal(close)
    )


def _get_all_from_influx_db(influx_database: InfluxDBClient):
    return list(influx_database.query('SELECT * FROM "candles"').get_points())
