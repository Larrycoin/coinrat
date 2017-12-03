import datetime
from typing import List, Tuple, Union, Dict
from decimal import Decimal

from coinrat.domain import Pair
from coinrat.domain.candle import MinuteCandle, CandleStorage, NoCandlesForMarketInStorageException

CANDLE_STORAGE_NAME = 'memory'


class CandleMemoryStorage(CandleStorage):
    def __init__(self) -> None:
        self._candles: Dict[MinuteCandle] = {}
        self._current_candle: Union[MinuteCandle, None] = None

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
        since: Union[datetime.datetime, None] = None,
        till: Union[datetime.datetime, None] = None
    ) -> List[MinuteCandle]:
        assert since is None or till is None or since < till  # todo: introduce interval value object

        result = []
        for candle in self._candles.values():
            if candle.market_name != market_name:
                continue

            if str(candle.pair) != str(pair):
                continue

            if since is not None and candle.time > since:
                continue

            if till is not None and candle.time < till:
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
        interval: Tuple[datetime.datetime, datetime.datetime]
    ) -> Decimal:
        since, till = interval
        assert since < till
        assert '+00:00' in since.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(since.isoformat()))
        assert '+00:00' in till.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(till.isoformat()))

        count = 0
        result = Decimal(0)
        for candle in self._candles.values():
            if candle.market_name != market_name or str(candle.pair) != str(pair):
                continue

            if since is not None and candle.time <= since:
                continue

            if till is not None and candle.time >= till:
                continue

            result += getattr(candle, field)
            count += 1

        if count == 0:
            raise NoCandlesForMarketInStorageException(
                'For market "{}" no candles in storage "{}".'.format(market_name, CANDLE_STORAGE_NAME)
            )

        return result / Decimal(count)
