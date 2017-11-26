from typing import List, Union

from .order import Order, Pair


class OrderStorage:
    def save_order(self, order: Order) -> None:
        raise NotImplementedError()

    def get_open_orders(self, market_name: str, pair: Pair) -> List[Order]:
        raise NotImplementedError()

    def find_last_order(self) -> Union[Order, None]:
        raise NotImplementedError()
