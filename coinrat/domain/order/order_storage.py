from typing import List, Union

from .order import Order, Pair
from coinrat.domain.datetime_interval import DateTimeInterval


class OrderStorage:
    @property
    def name(self) -> str:
        raise NotImplementedError()

    def save_order(self, order: Order) -> None:
        raise NotImplementedError()

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        status: str = None,
        direction: str = None,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> List[Order]:
        raise NotImplementedError()

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        raise NotImplementedError()

    def delete(self, order_id) -> None:
        raise NotImplementedError()
