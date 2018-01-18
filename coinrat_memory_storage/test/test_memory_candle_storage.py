from typing import Tuple

import pytest, datetime
from decimal import Decimal

from coinrat.domain import Pair, DateTimeInterval
from coinrat.domain.candle import MinuteCandle, CANDLE_STORAGE_FIELD_CLOSE, NoCandlesForMarketInStorageException
from coinrat_memory_storage.candle_storage import CandleMemoryStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')


def test_write_candles():
    storage = CandleMemoryStorage()

    storage.write_candles([_create_dummy_candle(1), _create_dummy_candle(2)])

    data = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(data) == 2
    assert data[0].time.isoformat() == "2017-07-02T00:01:00+00:00"
    assert data[1].time.isoformat() == '2017-07-02T00:02:00+00:00'


def test_write_zero_candles():
    storage = CandleMemoryStorage()
    storage.write_candles([])
    data = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(data) == 0


@pytest.mark.parametrize(['expected_mean', 'minute_interval'],
    [
        (8000, (0, 15)),
        (8300, (15, 30)),
        (8150, (0, 30)),
    ]
)
def test_mean(expected_mean: int, minute_interval: Tuple[int, int]):
    storage = CandleMemoryStorage()
    storage.write_candles([_create_dummy_candle(10, 8000), _create_dummy_candle(20, 8300)])
    interval = DateTimeInterval(
        datetime.datetime(2017, 7, 2, 0, minute_interval[0], 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2017, 7, 2, 0, minute_interval[1], 0, tzinfo=datetime.timezone.utc)
    )
    mean = storage.mean(DUMMY_MARKET, BTC_USD_PAIR, CANDLE_STORAGE_FIELD_CLOSE, interval)

    assert Decimal(expected_mean) == mean


def test_mean_no_data_raise_exception():
    """We want to raise exception to prevent invalid signal by dropping some price to 0."""
    storage = CandleMemoryStorage()
    interval = DateTimeInterval(
        datetime.datetime(2017, 7, 2, 0, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2017, 7, 2, 0, 30, 0, tzinfo=datetime.timezone.utc)
    )
    with pytest.raises(NoCandlesForMarketInStorageException):
        storage.mean(DUMMY_MARKET, BTC_USD_PAIR, CANDLE_STORAGE_FIELD_CLOSE, interval)


def test_get_current_candle():
    storage = CandleMemoryStorage()
    storage.write_candles([_create_dummy_candle(1, 8300)])

    candle = storage.get_last_candle(DUMMY_MARKET, BTC_USD_PAIR)
    assert candle.time.minute == 1

    storage.write_candles([_create_dummy_candle(2, 8300)])

    candle = storage.get_last_candle(DUMMY_MARKET, BTC_USD_PAIR)
    assert candle.time.minute == 2


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
