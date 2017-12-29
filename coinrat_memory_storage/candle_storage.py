import datetime
from typing import List, Tuple, Union, Dict
from decimal import Decimal

from coinrat.domain import Pair, DateTimeInterval
from coinrat.domain.candle import MinuteCandle, CandleStorage, NoCandlesForMarketInStorageException

CANDLE_STORAGE_NAME = 'memory'


class CandleMemoryStorage(CandleStorage):
    def __init__(self) -> None:
        self._candles: Dict[MinuteCandle] = {}
        self._current_candle: Union[MinuteCandle, None] = None

    @property
    def name(self) -> str:
        return CANDLE_STORAGE_NAME

    def write_candle(self, candle: MinuteCandle) -> None:
        self._candles[candle.time.isoformat()] = candle
        if self._current_candle is None or self._current_candle.time < candle.time:
            self._current_candle = candle

    def write_candles(self, candles: List[MinuteCandle]) -> None:
        for candle in candles:
            self.write_candle(candle)

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> List[MinuteCandle]:
        result = []
        for candle in self._candles.values():
            if candle.market_name != market_name:
                continue

            if str(candle.pair) != str(pair):
                continue

            if interval.since is not None and candle.time > interval.since:
                continue

            if interval.till is not None and candle.time < interval.till:
                continue

            result.append(candle)

        return result

    def get_current_candle(self, market_name: str, pair: Pair) -> MinuteCandle:
        return self._current_candle

    def mean(
        self,
        market_name: str,
        pair: Pair,
        field: str,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> Decimal:
        count = 0
        result = Decimal(0)
        for candle in self._candles.values():
            if candle.market_name != market_name or str(candle.pair) != str(pair):
                continue

            if interval.since is not None and candle.time <= interval.since:
                continue

            if interval.till is not None and candle.time >= interval.till:
                continue

            result += getattr(candle, field)
            count += 1

        if count == 0:
            raise NoCandlesForMarketInStorageException(
                'For market "{}" no candles in storage "{}".'.format(market_name, CANDLE_STORAGE_NAME)
            )

        return result / Decimal(count)
