import time
from ..market import MarketStateSynchronizer, MarketStorage, MarketPair
from .market import MARKET_BITREX, BittrexMarket


class BittrexSynchronizer(MarketStateSynchronizer):
    def __init__(self, market: BittrexMarket, storage: MarketStorage):
        self._storage = storage
        self._market = market

    def synchronize(self, pair: MarketPair):
        while True:
            candle = self._market.get_last_candle(pair)
            self._storage.write_candle(MARKET_BITREX, candle)
            time.sleep(30)
