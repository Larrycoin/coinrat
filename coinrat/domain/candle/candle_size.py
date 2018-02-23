import datetime

import math

from coinrat.domain import DateTimeInterval

CANDLE_SIZE_UNIT_MINUTE = 'minute'
CANDLE_SIZE_UNIT_HOUR = 'hour'
CANDLE_SIZE_UNIT_DAY = 'day'

UNIT_RANGES = {
    CANDLE_SIZE_UNIT_MINUTE: 60,
    CANDLE_SIZE_UNIT_HOUR: 24,
    CANDLE_SIZE_UNIT_DAY: 365,
}


class CandleSize:
    def __init__(self, unit: str, size: int) -> None:
        assert unit in [CANDLE_SIZE_UNIT_MINUTE, CANDLE_SIZE_UNIT_HOUR, CANDLE_SIZE_UNIT_DAY]

        if unit in [CANDLE_SIZE_UNIT_MINUTE, CANDLE_SIZE_UNIT_HOUR]:
            number_of_buckets = UNIT_RANGES[unit] / size
            assert number_of_buckets.is_integer(), \
                'For minute and hour candle-sizes, the whole range must be divisible to whole number!' \
                + ' But is: {}'.format(number_of_buckets)

        self.size = size
        self.unit = unit

    def assert_candle_time(self, time: datetime.datetime):
        assert '+00:00' in time.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(time.isoformat()))

        if self.unit in [CANDLE_SIZE_UNIT_MINUTE, CANDLE_SIZE_UNIT_HOUR, CANDLE_SIZE_UNIT_DAY]:
            assert time.second == 0
            assert time.microsecond == 0

        if self.unit in [CANDLE_SIZE_UNIT_HOUR, CANDLE_SIZE_UNIT_DAY]:
            assert time.minute == 0

        if self.unit == CANDLE_SIZE_UNIT_DAY:
            assert time.hour == 0

    def is_one_minute(self):
        return self.unit == CANDLE_SIZE_UNIT_MINUTE and self.size == 1

    def get_as_time_delta(self) -> datetime.timedelta:
        if self.unit == CANDLE_SIZE_UNIT_MINUTE:
            return datetime.timedelta(minutes=self.size)
        elif self.unit == CANDLE_SIZE_UNIT_HOUR:
            return datetime.timedelta(hours=self.size)
        elif self.unit == CANDLE_SIZE_UNIT_DAY:
            return datetime.timedelta(days=self.size)
        else:
            raise ValueError('Unknown unit "{}".'.format(self.unit))

    def get_interval_for_datetime(self, time: datetime.datetime) -> DateTimeInterval:
        time = time.replace(second=0)

        unit_range = UNIT_RANGES[self.unit]

        current_value = self._get_date_value_by_unit(time)
        number_of_buckets = unit_range / self.size
        bucket_number = int(math.floor(current_value / self.size))

        if bucket_number > number_of_buckets:
            raise ValueError('Bucket {} is higher than max number of buckets [{} ')

        value = bucket_number * self.size
        since = self._set_value_by_unit(time, value)
        till = since + self.get_as_time_delta()

        return DateTimeInterval(since, till)

    def _get_date_value_by_unit(self, time: datetime.datetime) -> int:
        if self.unit == CANDLE_SIZE_UNIT_MINUTE:
            return time.minute
        elif self.unit == CANDLE_SIZE_UNIT_HOUR:
            return time.hour
        elif self.unit == CANDLE_SIZE_UNIT_DAY:
            return time.timetuple().tm_yday
        else:
            raise ValueError('Unknown unit "{}".'.format(self.unit))

    def _set_value_by_unit(self, time: datetime.datetime, value: int) -> datetime.datetime:
        if self.unit == CANDLE_SIZE_UNIT_MINUTE:
            return time.replace(minute=value)
        elif self.unit == CANDLE_SIZE_UNIT_HOUR:
            return time.replace(minute=0, hour=value)
        elif self.unit == CANDLE_SIZE_UNIT_DAY:
            return time.replace(minute=0, hour=0, day=1, month=1) + datetime.timedelta(days=value)
        else:
            raise ValueError('Unknown unit "{}".'.format(self.unit))

    def __repr__(self):
        return 'CandleSize: ' + serialize_candle_size(self)


def serialize_candle_size(candle_size: CandleSize) -> str:
    return '{}-{}'.format(candle_size.size, candle_size.unit)


def deserialize_candle_size(serialized_candle_size: str) -> CandleSize:
    split_data = serialized_candle_size.split('-')
    return CandleSize(split_data[1], int(split_data[0]))
