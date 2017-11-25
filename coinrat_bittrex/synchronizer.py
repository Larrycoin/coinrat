import time
from typing import Union

from coinrat.domain import MarketStateSynchronizer, MarketsCandleStorage, MarketPair
from .market import BittrexMarket


class BittrexSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        market: BittrexMarket,
        storage: MarketsCandleStorage,
        delay: int = 30,
        number_of_runs: Union[int, None] = None
    ):
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._storage = storage
        self._market = market

    def synchronize(self, pair: MarketPair):
        self._import_historical_data(pair)

        while self._number_of_runs is None or self._number_of_runs > 0:

            candle = self._market.get_last_candle(pair)
            self._storage.write_candle(candle)

            if self._number_of_runs is not None:  # pragma: no cover
                self._number_of_runs -= 1

            time.sleep(self._delay)

    def _import_historical_data(self, pair: MarketPair):
        candles = self._market.get_candles(pair)
        self._storage.write_candles(candles)
