import datetime
from typing import List, Tuple, Union

from decimal import Decimal

from coinrat.domain.coinrat import ForEndUserException
from coinrat.domain.pair import Pair
from .candle import MinuteCandle

CANDLE_STORAGE_FIELD_OPEN = 'open'
CANDLE_STORAGE_FIELD_CLOSE = 'close'
CANDLE_STORAGE_FIELD_LOW = 'low'
CANDLE_STORAGE_FIELD_HIGH = 'high'
CANDLE_STORAGE_FIELD_MARKET = 'market'
CANDLE_STORAGE_FIELD_PAIR = 'pair'

class NoCandlesForMarketInStorageException(ForEndUserException):
    pass


class CandleStorage:
    def write_candle(self, candle: MinuteCandle) -> None:
        raise NotImplementedError()

    def write_candles(self, candles: List[MinuteCandle]) -> None:
        raise NotImplementedError()

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        since: Union[datetime.datetime, None] = None,
        till: Union[datetime.datetime, None] = None
    ) -> List[MinuteCandle]:
        raise NotImplementedError()

    def mean(
        self,
        market: str,
        pair: Pair,
        field: str,
        interval: Tuple[datetime.datetime, datetime.datetime]
    ) -> Decimal:
        raise NotImplementedError()

    def get_current_candle(self, market_name: str, pair: Pair) -> MinuteCandle:
        raise NotImplementedError()
