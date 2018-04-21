import datetime
from _pydecimal import Decimal
from typing import List

from coinrat.domain import DateTimeInterval

from coinrat.domain.candle import CandleSize, CandleStorage, Candle, CANDLE_SIZE_UNIT_MINUTE
from coinrat.domain.pair import Pair


class NullCandleStorage(CandleStorage):
    def write_candle(self, candle: Candle) -> None:
        pass

    def write_candles(self, candles: List[Candle]) -> None:
        pass

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval = DateTimeInterval(None, None),
        candle_size: CandleSize = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)
    ) -> List[Candle]:
        return []

    def mean(
        self,
        market: str,
        pair: Pair,
        field: str,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> Decimal:
        pass

    def get_last_minute_candle(self, market_name: str, pair: Pair, current_time: datetime.datetime) -> Candle:
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return 'null_candle_storage'
