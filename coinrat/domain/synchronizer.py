from .pair import Pair


class MarketStateSynchronizer:
    def synchronize(self, pair: Pair) -> None:
        raise NotImplementedError()
