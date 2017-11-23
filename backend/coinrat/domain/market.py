from decimal import Decimal

from .order import Order
from .pair import MarketPair


class Market:
    def get_name(self) -> str:
        raise NotImplementedError()

    @property
    def transaction_fee_coefficient(self):
        raise NotImplementedError()

    def get_balance(self, currency: str) -> Decimal:
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
