from .pair import MarketPair


class MarketStateSynchronizer:
    def synchronize(self, pair: MarketPair) -> None:
        raise NotImplementedError()
