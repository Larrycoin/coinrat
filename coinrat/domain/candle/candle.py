import datetime
from decimal import Decimal
from typing import Dict, List
import dateutil.parser

from coinrat.domain.pair import Pair, serialize_pair, deserialize_pair
from .candle_size import CandleSize, CANDLE_SIZE_UNIT_MINUTE, serialize_candle_size, deserialize_candle_size

CANDLE_STORAGE_FIELD_OPEN = 'open'
CANDLE_STORAGE_FIELD_CLOSE = 'close'
CANDLE_STORAGE_FIELD_LOW = 'low'
CANDLE_STORAGE_FIELD_HIGH = 'high'
CANDLE_STORAGE_FIELD_MARKET = 'market'
CANDLE_STORAGE_FIELD_PAIR = 'pair'
CANDLE_STORAGE_FIELD_SIZE = 'size'
CANDLE_STORAGE_FIELD_TIME = 'time'


class Candle:
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
        close_price: Decimal,
        candle_size: CandleSize = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)
    ) -> None:
        assert isinstance(open_price, Decimal)
        assert isinstance(high_price, Decimal)
        assert isinstance(low_price, Decimal)
        assert isinstance(close_price, Decimal)

        candle_size.assert_candle_time(time)

        self._market_name = market_name
        self._pair = pair
        self._time = time
        self._open = open_price
        self._high = high_price
        self._low = low_price
        self._close = close_price
        self._candle_size = candle_size

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

    @property
    def candle_size(self) -> CandleSize:
        return self._candle_size

    def __repr__(self):
        return '{0} O:{1:.8f} H:{2:.8f} L:{3:.8f} C:{4:.8f} | {5}' \
            .format(self._time.isoformat(), self._open, self._high, self._low, self._close, self._candle_size)


def serialize_candle(candle: Candle) -> Dict[str, str]:
    return {
        CANDLE_STORAGE_FIELD_MARKET: candle.market_name,
        CANDLE_STORAGE_FIELD_PAIR: serialize_pair(candle.pair),
        CANDLE_STORAGE_FIELD_TIME: candle.time.isoformat(),
        CANDLE_STORAGE_FIELD_OPEN: '{0:.8f}'.format(candle.open),
        CANDLE_STORAGE_FIELD_HIGH: '{0:.8f}'.format(candle.high),
        CANDLE_STORAGE_FIELD_LOW: '{0:.8f}'.format(candle.low),
        CANDLE_STORAGE_FIELD_CLOSE: '{0:.8f}'.format(candle.close),
        CANDLE_STORAGE_FIELD_SIZE: serialize_candle_size(candle.candle_size),
    }


def serialize_candles(candles: List[Candle]) -> List[Dict[str, str]]:
    return list(map(serialize_candle, candles))


def deserialize_candle(row: Dict) -> Candle:
    if CANDLE_STORAGE_FIELD_SIZE in row and row[CANDLE_STORAGE_FIELD_SIZE] is not None:
        candle_size = deserialize_candle_size(row[CANDLE_STORAGE_FIELD_SIZE])
    else:
        candle_size = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)

    return Candle(
        row[CANDLE_STORAGE_FIELD_MARKET],
        deserialize_pair(row[CANDLE_STORAGE_FIELD_PAIR]),
        dateutil.parser.parse(row[CANDLE_STORAGE_FIELD_TIME]).replace(tzinfo=datetime.timezone.utc),
        Decimal(row[CANDLE_STORAGE_FIELD_OPEN]),
        Decimal(row[CANDLE_STORAGE_FIELD_HIGH]),
        Decimal(row[CANDLE_STORAGE_FIELD_LOW]),
        Decimal(row[CANDLE_STORAGE_FIELD_CLOSE]),
        candle_size
    )


def deserialize_candles(serialized_candles: List[Dict[str, str]]) -> List[Candle]:
    return list(map(deserialize_candle, serialized_candles))
