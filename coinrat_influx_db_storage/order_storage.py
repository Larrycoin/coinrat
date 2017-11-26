from typing import Dict, List, Union
from uuid import UUID

from decimal import Decimal

import datetime
import dateutil.parser
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import OrderStorage, Order, Pair
from .utils import create_pair_identifier

ORDER_STORAGE_NAME = 'influx_db'

ORDER_STORAGE_FIELD_MARKET = 'market'
ORDER_STORAGE_FIELD_PAIR = 'pair'
ORDER_STORAGE_FIELD_ORDER_ID = 'order_id'
ORDER_STORAGE_FIELD_ID_ON_MARKET = 'id_on_market'
ORDER_STORAGE_FIELD_QUANTITY = 'quantity'
ORDER_STORAGE_FIELD_RATE = 'rate'
ORDER_STORAGE_FIELD_TYPE = 'type'
ORDER_STORAGE_FIELD_IS_OPEN = 'is_open'

MEASUREMENT_ORDERS_NAME = 'orders'


class OrderInnoDbStorage(OrderStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def save_order(self, order: Order) -> None:
        self._client.write_points([self._get_serialized_order(order)])

    def get_open_orders(self, market_name: str, pair: Pair) -> List[Order]:
        sql = '''
            SELECT * FROM "{}" WHERE "pair"='{}' AND "market"='{}' AND is_open = True
        '''.format(MEASUREMENT_ORDERS_NAME, create_pair_identifier(pair), market_name)

        result: ResultSet = self._client.query(sql)
        data = result.get_points()

        return [self._create_order_from_serialized(row) for row in data]

    @staticmethod
    def _get_serialized_order(order: Order) -> Dict:
        return {
            'measurement': MEASUREMENT_ORDERS_NAME,
            'tags': {
                ORDER_STORAGE_FIELD_MARKET: order.market_name,
                ORDER_STORAGE_FIELD_PAIR: create_pair_identifier(order.pair),
            },
            'time': order.created_at.isoformat(),
            'fields': {
                ORDER_STORAGE_FIELD_ORDER_ID: str(order.order_id),
                ORDER_STORAGE_FIELD_ID_ON_MARKET: order.id_on_market,
                ORDER_STORAGE_FIELD_TYPE: order.type,
                ORDER_STORAGE_FIELD_IS_OPEN: order.is_open,

                # Todo: figure out how to store decimals in influx (maybe int -> *100000)
                ORDER_STORAGE_FIELD_QUANTITY: float(order.quantity),
                ORDER_STORAGE_FIELD_RATE: float(order.rate),
            }
        }

    @staticmethod
    def _create_order_from_serialized(row: Dict[str, Union[str, int, float, bool]]) -> Order:
        pair_data = row[ORDER_STORAGE_FIELD_PAIR].split('_')

        return Order(
            UUID(row[ORDER_STORAGE_FIELD_ORDER_ID]),
            row[ORDER_STORAGE_FIELD_MARKET],
            dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc),
            Pair(pair_data[0], pair_data[1]),
            row[ORDER_STORAGE_FIELD_TYPE],
            Decimal(row[ORDER_STORAGE_FIELD_QUANTITY]),
            Decimal(row[ORDER_STORAGE_FIELD_RATE]) if row[ORDER_STORAGE_FIELD_RATE] is not None else None,
            row[ORDER_STORAGE_FIELD_ID_ON_MARKET],
            row[ORDER_STORAGE_FIELD_IS_OPEN],
        )
