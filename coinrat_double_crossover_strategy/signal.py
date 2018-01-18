from decimal import Decimal

SIGNAL_BUY = 'buy'
SIGNAL_SELL = 'sell'


class Signal:
    """
    Term used to describe point of view on the situation the market which is imperative to action (sell or buy)
    """

    def __init__(self, direction: str, average_price: Decimal) -> None:
        assert direction in [SIGNAL_BUY, SIGNAL_SELL]
        self._direction = direction
        self.average_price = average_price

    def is_buy(self):
        return self._direction == SIGNAL_BUY

    def is_sell(self):
        return self._direction == SIGNAL_SELL

    def __repr__(self) -> str:
        return self._direction
