from typing import Dict, List, Union
from uuid import UUID

from decimal import Decimal

import datetime
import dateutil.parser
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import OrderStorage, Order, Pair, POSSIBLE_ORDER_STATUSES
from .utils import create_pair_identifier

ORDER_STORAGE_NAME = 'influx_db'

ORDER_STORAGE_FIELD_MARKET = 'market'
ORDER_STORAGE_FIELD_DIRECTION = 'direction'
ORDER_STORAGE_FIELD_STATUS = 'status'
ORDER_STORAGE_FIELD_PAIR = 'pair'
ORDER_STORAGE_FIELD_ORDER_ID = 'order_id'
ORDER_STORAGE_FIELD_ID_ON_MARKET = 'id_on_market'
ORDER_STORAGE_FIELD_QUANTITY = 'quantity'
ORDER_STORAGE_FIELD_RATE = 'rate'
ORDER_STORAGE_FIELD_TYPE = 'type'

MEASUREMENT_ORDERS_NAME = 'orders'


class OrderInnoDbStorage(OrderStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def save_order(self, order: Order) -> None:
        self._client.write_points([self._get_serialized_order(order)])

    def find_by(self, market_name: str, pair: Pair, status: str = None, direction: str = None) -> List[Order]:
        assert status in POSSIBLE_ORDER_STATUSES or status is None, 'Invalid status: "{}"'.format(status)

        parameters = {
            ORDER_STORAGE_FIELD_MARKET: "'{}'".format(market_name),
            ORDER_STORAGE_FIELD_PAIR: "'{}'".format(create_pair_identifier(pair)),
        }
        if status is not None:
            parameters[ORDER_STORAGE_FIELD_STATUS] = "'{}'".format(status)
        if direction is not None:
            parameters[ORDER_STORAGE_FIELD_DIRECTION] = "'{}'".format(direction)

        sql = 'SELECT * FROM "{}" WHERE '.format(MEASUREMENT_ORDERS_NAME)
        where = []
        for key, value in parameters.items():
            where.append('"{}" = {}'.format(key, value))
        sql += ' AND '.join(where)
        result: ResultSet = self._client.query(sql)
        data = list(result.get_points())

        return [self._create_order_from_serialized(row) for row in data]

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        sql = '''
            SELECT * FROM "{}" WHERE "pair"='{}' AND "market"='{}' ORDER BY "time" DESC LIMIT 1
        '''.format(MEASUREMENT_ORDERS_NAME, create_pair_identifier(pair), market_name)

        result: ResultSet = self._client.query(sql)
        result = list(result.get_points())
        if len(result) == 0:
            return None

        return self._create_order_from_serialized(result[0])

    def delete(self, order_id) -> None:
        sql = '''
            DELETE FROM "{}" WHERE "order_id" = '{}'
        '''.format(MEASUREMENT_ORDERS_NAME, order_id)
        self._client.query(sql)

    @staticmethod
    def _get_serialized_order(order: Order) -> Dict:
        return {
            'measurement': MEASUREMENT_ORDERS_NAME,
            'tags': {
                ORDER_STORAGE_FIELD_MARKET: order.market_name,
                ORDER_STORAGE_FIELD_PAIR: create_pair_identifier(order.pair),
                ORDER_STORAGE_FIELD_ORDER_ID: str(order.order_id),
            },
            'time': order.created_at.isoformat(),
            'fields': {
                ORDER_STORAGE_FIELD_DIRECTION: order._direction,
                ORDER_STORAGE_FIELD_ID_ON_MARKET: order.id_on_market,
                ORDER_STORAGE_FIELD_TYPE: order.type,
                ORDER_STORAGE_FIELD_STATUS: order._status,

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
            row[ORDER_STORAGE_FIELD_DIRECTION],
            dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc),
            Pair(pair_data[0], pair_data[1]),
            row[ORDER_STORAGE_FIELD_TYPE],
            Decimal(row[ORDER_STORAGE_FIELD_QUANTITY]),
            Decimal(row[ORDER_STORAGE_FIELD_RATE]) if row[ORDER_STORAGE_FIELD_RATE] is not None else None,
            row[ORDER_STORAGE_FIELD_ID_ON_MARKET],
            row[ORDER_STORAGE_FIELD_STATUS],
        )
