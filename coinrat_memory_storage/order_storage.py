from typing import Dict, List, Union

from coinrat.domain import Pair, DateTimeInterval
from coinrat.domain.order import OrderStorage, Order, POSSIBLE_ORDER_STATUSES

ORDER_STORAGE_NAME = 'memory'


class OrderMemoryStorage(OrderStorage):
    def __init__(self) -> None:
        self._orders: Dict[Order] = {}
        self._last_order: Union[Order, None] = None

    @property
    def name(self) -> str:
        return ORDER_STORAGE_NAME

    def save_order(self, order: Order) -> None:
        self._orders[str(order.order_id)] = order

        if self._last_order is None or self._last_order.created_at <= order.created_at:
            self._last_order = order

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        status: str = None,
        direction: str = None,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> List[Order]:
        assert status in POSSIBLE_ORDER_STATUSES or status is None, 'Invalid status: "{}"'.format(status)

        result = []
        for order in self._orders.values():
            if order.market_name != market_name or str(order.pair) != str(pair):
                continue

            if status is not None and order._status != status:
                continue

            if direction is not None and order._direction != direction:
                continue

            if interval.since is not None and order.created_at <= interval.since:
                continue

            if interval.till is not None and order.created_at >= interval.till:
                continue

            result.append(order)

        return result

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        return self._last_order

    def delete(self, order_id) -> None:
        self._orders.pop(order_id, None)
