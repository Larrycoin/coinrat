import json

from coinrat.domain.datetime_interval import DateTimeInterval
from coinrat.domain.pair import Pair
from coinrat.domain.order import serialize_orders, deserialize_orders
from .order_storage import OrderStorage


class OrderExporter:
    def __init__(self, order_storage: OrderStorage) -> None:
        self._order_storage = order_storage

    def export_to_file(
        self,
        filename: str,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ):
        orders = self._order_storage.find_by(market_name=market_name, pair=pair, interval=interval)
        data = serialize_orders(orders)

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def import_from_file(self, filename: str):
        with open(filename) as json_file:
            data = json.load(json_file)
            orders = deserialize_orders(data)
            for order in orders:
                self._order_storage.save_order(order)
