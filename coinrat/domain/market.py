from decimal import Decimal
from typing import Union

from .order import Order
from .pair import MarketPair


class PairMarketInfo:
    def __init__(self, pair: MarketPair, minimal_order_size: Union[Decimal, None]) -> None:
        self._pair = pair
        self._minimal_order_size = minimal_order_size

    @property
    def pair(self):
        return self._pair

    @property
    def minimal_order_size(self):
        return self._minimal_order_size

    def __repr__(self) -> str:
        return 'Pair: [{0}], minimal order size: {1:.8}'.format(self._pair, self._minimal_order_size)


class Market:
    def get_name(self) -> str:
        raise NotImplementedError()

    @property
    def transaction_fee_coefficient(self):
        raise NotImplementedError()

    def get_balance(self, currency: str) -> Decimal:
        raise NotImplementedError()

    def get_pair_market_info(self, pair: MarketPair) -> PairMarketInfo:
        raise NotImplementedError()

    def create_sell_order(self, order: Order) -> str:
        raise NotImplementedError()

    def create_buy_order(self, order: Order) -> str:
        raise NotImplementedError()

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError()

    def buy_max_available(self, pair: MarketPair) -> str:
        raise NotImplementedError()

    def sell_max_available(self, pair: MarketPair) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.get_name()
