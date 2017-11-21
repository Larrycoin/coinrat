from coinrat_market import Market, MarketPair
from market_storage import MarketStorage
import time


class MarketSynchronizer:
    def __init__(self, storage: MarketStorage, market: Market) -> None:
        self._storage = storage
        self._market = market

    def run(self, pair: MarketPair):
        while True:
            candle = self._market.get_last_candle(pair)
            self._storage.write_candle(self._market.get_id(), candle)
            time.sleep(30)
