import datetime

import pytest

from coinrat.domain.candle import CandleSize, CANDLE_SIZE_UNIT_MINUTE, CANDLE_SIZE_UNIT_HOUR, CANDLE_SIZE_UNIT_DAY


def test_get_as_time_delta():
    candle_size = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 15)
    assert candle_size.get_as_time_delta() == datetime.timedelta(minutes=15)


@pytest.mark.parametrize(
    ['expected', 'candle_size', 'time'],
    [
        [
            '[2018-01-01T00:00:00+00:00, 2018-01-01T00:15:00+00:00]',
            CandleSize(CANDLE_SIZE_UNIT_MINUTE, 15),
            datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        ],
        [
            '[2018-01-01T00:00:00+00:00, 2018-01-01T00:15:00+00:00]',
            CandleSize(CANDLE_SIZE_UNIT_MINUTE, 15),
            datetime.datetime(2018, 1, 1, 0, 4, 0, tzinfo=datetime.timezone.utc)
        ],
        [
            '[2018-01-01T00:15:00+00:00, 2018-01-01T00:30:00+00:00]',
            CandleSize(CANDLE_SIZE_UNIT_MINUTE, 15),
            datetime.datetime(2018, 1, 1, 0, 15, 24, tzinfo=datetime.timezone.utc)
        ],
        [
            '[2018-01-01T08:00:00+00:00, 2018-01-01T12:00:00+00:00]',
            CandleSize(CANDLE_SIZE_UNIT_HOUR, 4),
            datetime.datetime(2018, 1, 1, 9, 15, 24, tzinfo=datetime.timezone.utc)
        ],
        [
            '[2018-01-01T00:00:00+00:00, 2018-01-08T00:00:00+00:00]',
            CandleSize(CANDLE_SIZE_UNIT_DAY, 7),
            datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        ],
        [
            '[2018-02-26T00:00:00+00:00, 2018-03-05T00:00:00+00:00]',
            CandleSize(CANDLE_SIZE_UNIT_DAY, 7),
            datetime.datetime(2018, 2, 27, 0, 24, 24, tzinfo=datetime.timezone.utc)
        ],
    ],
)
def test_get_interval_for_datetime(expected: str, candle_size: CandleSize, time: datetime.datetime):
    assert str(candle_size.get_interval_for_datetime(time)) == expected


@pytest.mark.parametrize(
    ['unit', 'size'],
    [
        (CANDLE_SIZE_UNIT_HOUR, 5),
        (CANDLE_SIZE_UNIT_MINUTE, 7),
    ],
)
def test_get_interval_for_datetime_non_divisible_values_raises_error(unit: str, size: int):
    with pytest.raises(AssertionError):
        CandleSize(unit, size)
