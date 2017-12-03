import datetime
import json
import dateutil.parser
from typing import Dict

from decimal import Decimal
from coinrat.domain.datetime_interval import DateTimeInterval
from coinrat.domain.pair import Pair
from coinrat.domain.order import Order, ORDER_FIELD_MARKET, ORDER_FIELD_DIRECTION, \
    ORDER_FIELD_STATUS, ORDER_FIELD_PAIR, ORDER_FIELD_ORDER_ID, ORDER_FIELD_ID_ON_MARKET, ORDER_FIELD_QUANTITY, \
    ORDER_FIELD_RATE, ORDER_FIELD_TYPE, ORDER_FIELD_CREATED_AT, ORDER_FIELD_CLOSED_AT, ORDER_FIELD_CANCELED_AT
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
        data = list(map(self._serialize_order_to_json_serializable, orders))

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def import_from_file(self, filename: str):
        with open(filename) as json_file:
            data = json.load(json_file)
            orders = list(map(self._create_order_from_data, data))
            for order in orders:
                self._order_storage.save_order(order)

    @staticmethod
    def _serialize_order_to_json_serializable(order: Order):
        return {
            ORDER_FIELD_ORDER_ID: str(order.order_id),
            ORDER_FIELD_MARKET: order.market_name,
            ORDER_FIELD_DIRECTION: order._direction,
            ORDER_FIELD_CREATED_AT: order.created_at.isoformat(),
            ORDER_FIELD_PAIR: OrderExporter._create_pair_identifier(order.pair),
            ORDER_FIELD_TYPE: order.type,
            ORDER_FIELD_QUANTITY: str(order.quantity),
            ORDER_FIELD_RATE: str(order.rate),
            ORDER_FIELD_ID_ON_MARKET: order.id_on_market,
            ORDER_FIELD_STATUS: order._status,
            ORDER_FIELD_CLOSED_AT: order.closed_at.isoformat() if order.closed_at is not None else None,
            ORDER_FIELD_CANCELED_AT: order.canceled_at.isoformat() if order.canceled_at is not None else None,
        }

    @staticmethod
    def _create_order_from_data(row: Dict) -> Order:
        closed_at = row[ORDER_FIELD_CLOSED_AT]
        if closed_at is not None:
            closed_at = dateutil.parser.parse(closed_at).replace(tzinfo=datetime.timezone.utc)

        canceled_at = row[ORDER_FIELD_CANCELED_AT]
        if canceled_at is not None:
            canceled_at = dateutil.parser.parse(canceled_at).replace(tzinfo=datetime.timezone.utc)

        return Order(
            row[ORDER_FIELD_ORDER_ID],
            row[ORDER_FIELD_MARKET],
            row[ORDER_FIELD_DIRECTION],
            dateutil.parser.parse(row[ORDER_FIELD_CREATED_AT]).replace(tzinfo=datetime.timezone.utc),
            OrderExporter._create_pair_from_identifier(row[ORDER_FIELD_PAIR]),
            row[ORDER_FIELD_TYPE],
            Decimal(row[ORDER_FIELD_QUANTITY]),
            Decimal(row[ORDER_FIELD_RATE]),
            row[ORDER_FIELD_ID_ON_MARKET],
            row[ORDER_FIELD_STATUS],
            closed_at,
            canceled_at
        )

    @staticmethod
    def _create_pair_identifier(pair: Pair) -> str:
        return '{}_{}'.format(pair.base_currency, pair.market_currency)

    @staticmethod
    def _create_pair_from_identifier(identifier: str) -> Pair:
        return Pair(*identifier.split('_'))
