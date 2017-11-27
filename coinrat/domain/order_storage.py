from typing import List, Union

from .order import Order, Pair


class OrderStorage:
    def save_order(self, order: Order) -> None:
        raise NotImplementedError()

    def find_by(self, market_name: str, pair: Pair, is_open: bool = None, direction: str = None) -> List[Order]:
        raise NotImplementedError()

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        raise NotImplementedError()
