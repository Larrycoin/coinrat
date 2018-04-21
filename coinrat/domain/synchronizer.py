from typing import List

from .pair.pair import Pair


class MarketStateSynchronizer:
    def synchronize(self, market_name: str, pair: Pair) -> None:
        raise NotImplementedError()

    def get_supported_markets(self) -> List[str]:
        raise NotImplementedError()
