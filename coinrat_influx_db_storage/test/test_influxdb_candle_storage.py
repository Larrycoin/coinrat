from typing import Tuple

import pytest, datetime
from flexmock import flexmock
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import Pair, DateTimeInterval
from coinrat.domain.candle import Candle, CANDLE_STORAGE_FIELD_CLOSE, NoCandlesForMarketInStorageException
from coinrat_influx_db_storage.candle_storage import CandleInnoDbStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


def test_write_candle(influx_database: InfluxDBClient):
    storage = CandleInnoDbStorage(influx_database)

    storage.write_candle(_create_dummy_candle())

    data = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(data) == 1
    assert '2017-07-02T00:00:00+00:00 O:8000.00000000 H:8100.00000000 L:8200.00000000 C:8300.00000000 ' + \
           '| CandleSize: 1-minute' == str(data[0])


def test_write_candles(influx_database: InfluxDBClient):
    storage = CandleInnoDbStorage(influx_database)

    storage.write_candles([_create_dummy_candle(1), _create_dummy_candle(2)])

    data = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(data) == 2
    assert data[0].time.isoformat() == '2017-07-02T00:01:00+00:00'
    assert data[1].time.isoformat() == '2017-07-02T00:02:00+00:00'


def test_write_zero_candles():
    mock_influx_database = flexmock()
    mock_influx_database.should_receive('write_points').never()

    storage = CandleInnoDbStorage(mock_influx_database)
    storage.write_candles([])


@pytest.mark.parametrize(['expected_mean', 'minute_interval'],
    [
        (8000, (0, 15)),
        (8300, (15, 30)),
        (8150, (0, 30)),
    ]
)
def test_mean(influx_database: InfluxDBClient, expected_mean: int, minute_interval: Tuple[int, int]):
    storage = CandleInnoDbStorage(influx_database)
    storage.write_candles([_create_dummy_candle(10, 8000), _create_dummy_candle(20, 8300)])
    interval = DateTimeInterval(
        datetime.datetime(2017, 7, 2, 0, minute_interval[0], 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2017, 7, 2, 0, minute_interval[1], 0, tzinfo=datetime.timezone.utc)
    )
    mean = storage.mean(DUMMY_MARKET, BTC_USD_PAIR, CANDLE_STORAGE_FIELD_CLOSE, interval)

    assert Decimal(expected_mean) == mean


def test_mean_no_data_raise_exception(influx_database: InfluxDBClient):
    """We want to raise exception to prevent invalid signal by dropping some price to 0."""
    storage = CandleInnoDbStorage(influx_database)
    interval = DateTimeInterval(
        datetime.datetime(2017, 7, 2, 0, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2017, 7, 2, 0, 30, 0, tzinfo=datetime.timezone.utc)
    )
    with pytest.raises(NoCandlesForMarketInStorageException):
        storage.mean(DUMMY_MARKET, BTC_USD_PAIR, CANDLE_STORAGE_FIELD_CLOSE, interval)


def test_get_last_minute_candle(influx_database: InfluxDBClient):
    storage = CandleInnoDbStorage(influx_database)
    storage.write_candles([_create_dummy_candle(1, 8300)])

    current_time = datetime.datetime(2017, 7, 2, 1, 0, 0, tzinfo=datetime.timezone.utc)

    candle = storage.get_last_minute_candle(DUMMY_MARKET, BTC_USD_PAIR, current_time)
    assert candle.time.minute == 1

    storage.write_candles([_create_dummy_candle(2, 8300)])

    candle = storage.get_last_minute_candle(DUMMY_MARKET, BTC_USD_PAIR, current_time)
    assert candle.time.minute == 2


def _create_dummy_candle(minute: int = 0, close: int = 8300) -> Candle:
    return Candle(
        DUMMY_MARKET,
        BTC_USD_PAIR,
        datetime.datetime(2017, 7, 2, 0, minute, 0, tzinfo=datetime.timezone.utc),
        Decimal(8000),
        Decimal(8100),
        Decimal(8200),
        Decimal(close)
    )
