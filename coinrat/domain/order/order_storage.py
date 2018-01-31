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
        status: Union[str, None] = None,
        direction: Union[str, None] = None,
        interval: DateTimeInterval = DateTimeInterval(None, None),
        strategy_run_id: Union[str, None] = None
    ) -> List[Order]:
        raise NotImplementedError()

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        raise NotImplementedError()

    def delete(self, order_id) -> None:
        raise NotImplementedError()

    def delete_by(
        self,
        market_name: str,
        pair: Pair,
        status: str = None,
        direction: str = None,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ):
        orders = self.find_by(market_name, pair, status, direction, interval)
        for order in orders:
            self.delete(order.order_id)
