import datetime
from decimal import Decimal
from typing import List

from coinrat.domain import DateTimeInterval
from .candle import Candle
from .candle_size import CandleSize, CANDLE_SIZE_UNIT_MINUTE
from coinrat.domain.pair import Pair
from coinrat.domain.coinrat import ForEndUserException


class NoCandlesForMarketInStorageException(ForEndUserException):
    pass


class CandleStorage:
    def write_candle(self, candle: Candle) -> None:
        raise NotImplementedError()

    def write_candles(self, candles: List[Candle]) -> None:
        raise NotImplementedError()

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval = DateTimeInterval(None, None),
        candle_size: CandleSize = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)
    ) -> List[Candle]:
        raise NotImplementedError()

    def mean(
        self,
        market: str,
        pair: Pair,
        field: str,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> Decimal:
        raise NotImplementedError()

    def get_last_minute_candle(self, market_name: str, pair: Pair, current_time: datetime.datetime) -> Candle:
        raise NotImplementedError()

    @property
    def name(self) -> str:
        raise NotImplementedError()
