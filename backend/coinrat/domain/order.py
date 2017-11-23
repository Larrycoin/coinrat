from decimal import Decimal
from typing import Union

from .pair import MarketPair

ORDER_TYPE_LIMIT = 'limit'
ORDER_TYPE_MARKET = 'market'


class Order:
    def __init__(self, pair: MarketPair, order_type: str, quantity: Decimal, rate: Union[Decimal, None] = None) -> None:
        assert order_type in [ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET]
        assert isinstance(quantity, Decimal)

        if order_type == ORDER_TYPE_LIMIT:
            assert isinstance(rate, Decimal)
        if order_type == ORDER_TYPE_MARKET:
            assert rate is None

        self._pair = pair
        self._type = order_type
        self._quantity = quantity
        self._rate = rate

    @property
    def pair(self) -> MarketPair:
        return self._pair

    @property
    def type(self) -> str:
        return self._type

    @property
    def rate(self) -> Union[Decimal, None]:
        return self._rate

    @property
    def quantity(self) -> Decimal:
        return self._quantity

    def __repr__(self) -> str:
        return 'Pair: [{}], type: "{}", rate: {}, quantity: {}' \
            .format(self._pair, self._type, self._rate, self._quantity)
