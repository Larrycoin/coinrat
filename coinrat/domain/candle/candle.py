import datetime
from decimal import Decimal
from typing import Dict, List
import dateutil.parser

from coinrat.domain.pair import Pair, serialize_pair, deserialize_pair

CANDLE_STORAGE_FIELD_OPEN = 'open'
CANDLE_STORAGE_FIELD_CLOSE = 'close'
CANDLE_STORAGE_FIELD_LOW = 'low'
CANDLE_STORAGE_FIELD_HIGH = 'high'
CANDLE_STORAGE_FIELD_MARKET = 'market'
CANDLE_STORAGE_FIELD_PAIR = 'pair'


class MinuteCandle:
    """
    OPEN, CLOSE: The open and close prices are the first and last transaction prices for that time period (minute).

    LOW, HIGH: The high price is the highest price reached during a specific time period. The low price is the lowest
    price reached during a specific period (minute).
    """

    def __init__(
        self,
        market_name:
        str,
        pair: Pair,
        time: datetime.datetime,
        open_price: Decimal,
        high_price: Decimal,
        low_price: Decimal,
        close_price: Decimal
    ) -> None:
        assert isinstance(open_price, Decimal)
        assert isinstance(high_price, Decimal)
        assert isinstance(low_price, Decimal)
        assert isinstance(close_price, Decimal)

        assert time.second == 0
        assert time.microsecond == 0

        assert '+00:00' in time.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(time.isoformat()))

        self._market_name = market_name
        self._pair = pair
        self._time = time
        self._open = open_price
        self._high = high_price
        self._low = low_price
        self._close = close_price

    @property
    def pair(self) -> Pair:
        return self._pair

    @property
    def market_name(self) -> str:
        return self._market_name

    @property
    def time(self) -> datetime.datetime:
        return self._time

    @property
    def open(self) -> Decimal:
        return self._open

    @property
    def close(self) -> Decimal:
        return self._close

    @property
    def low(self) -> Decimal:
        return self._low

    @property
    def high(self) -> Decimal:
        return self._high

    @property
    def average_price(self) -> Decimal:
        return (self._low + self._high) / 2

    def __repr__(self):
        return '{0} O:{1:.8f} H:{2:.8f} L:{3:.8f} C:{4:.8f}' \
            .format(self._time.isoformat(), self._open, self._high, self._low, self._close)


def serialize_candle(candle: MinuteCandle) -> Dict[str, str]:
    return {
        'market': candle.market_name,
        'pair': serialize_pair(candle.pair),
        'time': candle.time.isoformat(),
        CANDLE_STORAGE_FIELD_OPEN: str(candle.open),
        CANDLE_STORAGE_FIELD_HIGH: str(candle.high),
        CANDLE_STORAGE_FIELD_LOW: str(candle.low),
        CANDLE_STORAGE_FIELD_CLOSE: str(candle.close),
    }


def serialize_candles(candles: List[MinuteCandle]) -> List[Dict[str, str]]:
    return list(map(serialize_candle, candles))


def deserialize_candle(row: Dict) -> MinuteCandle:
    return MinuteCandle(
        row['market'],
        deserialize_pair(row['pair']),
        dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc),
        Decimal(row[CANDLE_STORAGE_FIELD_OPEN]),
        Decimal(row[CANDLE_STORAGE_FIELD_HIGH]),
        Decimal(row[CANDLE_STORAGE_FIELD_LOW]),
        Decimal(row[CANDLE_STORAGE_FIELD_CLOSE])
    )


def deserialize_candles(serialized_candles: List[Dict[str, str]]) -> List[MinuteCandle]:
    return list(map(deserialize_candle, serialized_candles))
