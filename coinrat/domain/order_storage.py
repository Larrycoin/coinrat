from typing import List

from .order import Order, Pair


class OrderStorage:
    def save_order(self, order: Order) -> None:
        raise NotImplementedError()

    def get_open_orders(self, market_name: str, pair: Pair) -> List[Order]:
        raise NotImplementedError()
