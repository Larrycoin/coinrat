from typing import Dict

from influxdb import InfluxDBClient

from coinrat.domain import OrderStorage, Order
from .utils import create_pair_identifier

ORDER_STORAGE_NAME = 'influx_db'


class OrderInnoDbStorage(OrderStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def save_order(self, order: Order) -> None:
        self._client.write_points(self._get_serialized_order(order))

    def _get_serialized_order(self, order: Order) -> Dict:
        return {
            "measurement": "orders",
            "tags": {
                "market": order.market_name,
                "pair": create_pair_identifier(order.pair),
            },
            "time": order.time.isoformat(),
            "fields": {
                # Todo: figure out how to store decimals in influx (maybe int -> *100000)
                CANDLE_STORAGE_FIELD_OPEN: float(order.open),
                CANDLE_STORAGE_FIELD_CLOSE: float(order.close),
                CANDLE_STORAGE_FIELD_LOW: float(order.low),
                CANDLE_STORAGE_FIELD_HIGH: float(order.high),
            }
        }
