from typing import Dict, List, Union
from uuid import UUID

from decimal import Decimal

import datetime
import dateutil.parser
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import Pair, DateTimeInterval, serialize_pair
from coinrat.domain.order import OrderStorage, Order, POSSIBLE_ORDER_STATUSES
from coinrat.domain.order import ORDER_FIELD_MARKET, ORDER_FIELD_PAIR, ORDER_FIELD_STATUS, \
    ORDER_FIELD_DIRECTION, ORDER_FIELD_ORDER_ID, ORDER_FIELD_QUANTITY, ORDER_FIELD_CANCELED_AT, \
    ORDER_FIELD_RATE, ORDER_FIELD_ID_ON_MARKET, ORDER_FIELD_TYPE, ORDER_FIELD_CLOSED_AT

ORDER_STORAGE_NAME = 'influx_db'

MEASUREMENT_ORDERS_NAME = 'orders'


class OrderInnoDbStorage(OrderStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    @property
    def name(self) -> str:
        return ORDER_STORAGE_NAME

    def save_order(self, order: Order) -> None:
        self._client.write_points([self._get_serialized_order(order)])

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        status: str = None,
        direction: str = None,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> List[Order]:
        assert status in POSSIBLE_ORDER_STATUSES or status is None, 'Invalid status: "{}"'.format(status)

        parameters = {
            ORDER_FIELD_MARKET: "= '{}'".format(market_name),
            ORDER_FIELD_PAIR: "= '{}'".format(serialize_pair(pair)),
        }

        if status is not None:
            parameters[ORDER_FIELD_STATUS] = "= '{}'".format(status)
        if direction is not None:
            parameters[ORDER_FIELD_DIRECTION] = "= '{}'".format(direction)
        if interval.since is not None:
            parameters['"time" >'] = "'{}'".format(interval.since.isoformat())
        if interval.till is not None:
            parameters['"time" <'] = "'{}'".format(interval.till.isoformat())

        sql = 'SELECT * FROM "{}" WHERE '.format(MEASUREMENT_ORDERS_NAME)
        where = []
        for key, value in parameters.items():
            where.append('{} {}'.format(key, value))
        sql += ' AND '.join(where)
        result: ResultSet = self._client.query(sql)
        data = list(result.get_points())

        return [self._create_order_from_serialized(row) for row in data]

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        sql = '''
            SELECT * FROM "{}" WHERE "pair"='{}' AND "market"='{}' ORDER BY "time" DESC LIMIT 1
        '''.format(MEASUREMENT_ORDERS_NAME, serialize_pair(pair), market_name)

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
                ORDER_FIELD_MARKET: order.market_name,
                ORDER_FIELD_PAIR: serialize_pair(order.pair),
                ORDER_FIELD_ORDER_ID: str(order.order_id),
            },
            'time': order.created_at.isoformat(),
            'fields': {
                ORDER_FIELD_DIRECTION: order._direction,
                ORDER_FIELD_ID_ON_MARKET: order.id_on_market,
                ORDER_FIELD_TYPE: order.type,
                ORDER_FIELD_STATUS: order._status,

                # Todo: figure out how to store decimals in influx (maybe int -> *100000)
                ORDER_FIELD_QUANTITY: float(order.quantity),
                ORDER_FIELD_RATE: float(order.rate),

                ORDER_FIELD_CLOSED_AT: order.closed_at.isoformat() if order.closed_at is not None else None,
                ORDER_FIELD_CANCELED_AT: order.canceled_at.isoformat() if order.canceled_at is not None else None,
            }
        }

    @staticmethod
    def _create_order_from_serialized(row: Dict[str, Union[str, int, float, bool]]) -> Order:
        pair_data = row[ORDER_FIELD_PAIR].split('_')

        closed_at = None
        if ORDER_FIELD_CLOSED_AT in row and row[ORDER_FIELD_CLOSED_AT] is not None:
            closed_at = dateutil.parser.parse(row[ORDER_FIELD_CLOSED_AT]).replace(tzinfo=datetime.timezone.utc)

        canceled_at = None
        if ORDER_FIELD_CANCELED_AT in row and row[ORDER_FIELD_CANCELED_AT] is not None:
            canceled_at = dateutil.parser.parse(row[ORDER_FIELD_CANCELED_AT]).replace(tzinfo=datetime.timezone.utc)

        return Order(
            UUID(row[ORDER_FIELD_ORDER_ID]),
            row[ORDER_FIELD_MARKET],
            row[ORDER_FIELD_DIRECTION],
            dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc),
            Pair(pair_data[0], pair_data[1]),
            row[ORDER_FIELD_TYPE],
            Decimal(row[ORDER_FIELD_QUANTITY]),
            Decimal(row[ORDER_FIELD_RATE]) if ORDER_FIELD_RATE in row is not None else None,
            row[ORDER_FIELD_ID_ON_MARKET] if ORDER_FIELD_ID_ON_MARKET in row is not None else None,
            row[ORDER_FIELD_STATUS],
            closed_at,
            canceled_at
        )
