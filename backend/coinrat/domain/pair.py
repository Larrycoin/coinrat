class MarketPair:
    def __init__(self, left: str, right: str) -> None:
        assert left != 'USDT', \
            'Some markets use USDT instead of USD, this is impl. detail of that market, use USD otherwise'
        assert right not in ['USDT', 'USD'], 'This is probably error. Pairs are not usually represented in USD as right'

        self._left = left
        self._right = right

    @property
    def left(self) -> str:
        return self._left

    @property
    def right(self) -> str:
        return self._right

    def __repr__(self):
        return '{}-{}'.format(self._left, self._right)
