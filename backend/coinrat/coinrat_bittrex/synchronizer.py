import time
from typing import Union

from ..market import MarketStateSynchronizer, MarketStorage, MarketPair
from .market import MARKET_BITREX, BittrexMarket


class BittrexSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        market: BittrexMarket,
        storage: MarketStorage,
        delay: int = 30,
        number_of_runs: Union[int, None] = None
    ):
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._storage = storage
        self._market = market

    def synchronize(self, pair: MarketPair):
        while self._number_of_runs is None or self._number_of_runs > 0:

            candle = self._market.get_last_candle(pair)
            self._storage.write_candle(MARKET_BITREX, pair, candle)

            if self._number_of_runs is not None:
                self._number_of_runs -= 1
            time.sleep(self._delay)
