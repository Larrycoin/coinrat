import datetime
from typing import List, Tuple

from decimal import Decimal

from .coinrat import ForEndUserException
from .candle import MinuteCandle
from .pair import MarketPair

CANDLE_STORAGE_FIELD_OPEN = 'open'
CANDLE_STORAGE_FIELD_CLOSE = 'close'
CANDLE_STORAGE_FIELD_LOW = 'low'
CANDLE_STORAGE_FIELD_HIGH = 'high'


class NoCandlesForMarketInStorageException(ForEndUserException):
    pass


class CandleStorage:
    def write_candle(self, candle: MinuteCandle) -> None:
        raise NotImplementedError()

    def write_candles(self, candles: List[MinuteCandle]) -> None:
        raise NotImplementedError()

    def mean(
        self,
        market: str,
        pair: MarketPair,
        field: str,
        interval: Tuple[datetime.datetime, datetime.datetime]
    ) -> Decimal:
        raise NotImplementedError()
