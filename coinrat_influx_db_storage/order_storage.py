from typing import Dict

from influxdb import InfluxDBClient

from coinrat.domain import OrderStorage, Order
from .utils import create_pair_identifier

ORDER_STORAGE_NAME = 'influx_db'

ORDER_STORAGE_FIELD_ORDER_ID = 'order_id'
ORDER_STORAGE_FIELD_ID_ON_MARKET = 'id_on_market'
ORDER_STORAGE_FIELD_QUANTITY = 'quantity'
ORDER_STORAGE_FIELD_RATE = 'rate'
ORDER_STORAGE_FIELD_TYPE = 'type'


class OrderInnoDbStorage(OrderStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def save_order(self, order: Order) -> None:
        self._client.write_points(self._get_serialized_order(order))

    @staticmethod
    def _get_serialized_order(order: Order) -> Dict:
        return {
            'measurement': 'orders',
            'tags': {
                'market': order.market_name,
                'pair': create_pair_identifier(order.pair),
            },
            'time': order.created_at.isoformat(),
            'fields': {
                ORDER_STORAGE_FIELD_ORDER_ID: str(order.order_id),
                ORDER_STORAGE_FIELD_ID_ON_MARKET: order.id_on_market,

                # Todo: figure out how to store decimals in influx (maybe int -> *100000)
                ORDER_STORAGE_FIELD_QUANTITY: float(order.quantity),
                ORDER_STORAGE_FIELD_RATE: float(order.rate),
                ORDER_STORAGE_FIELD_TYPE: float(order.type),
            }
        }
