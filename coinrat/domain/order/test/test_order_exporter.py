import datetime
import json

import os
from uuid import UUID

from flexmock import flexmock
from decimal import Decimal

from coinrat.domain.order import Order, OrderExporter, DIRECTION_BUY, ORDER_TYPE_LIMIT
from coinrat.domain import Pair

DUMMY_MARKET = 'dummy_market_name'


def test_order_export_import():
    pair = Pair('USD', 'BTC')
    order = Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
        DUMMY_MARKET,
        DIRECTION_BUY,
        datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
        pair,
        ORDER_TYPE_LIMIT,
        Decimal('1'),
        Decimal('8000'),
        'aaa-id-from-market'
    )

    storage = flexmock()
    storage.should_receive('find_by').and_return([order]).once()
    storage.should_receive('save_order').once()
    exporter = OrderExporter(storage)
    file_name = os.path.dirname(__file__) + '_orders.json'

    exporter.export_to_file(file_name, 'dummy_market', pair)

    expected = [{
        "order_id": "16fd2706-8baf-433b-82eb-8c7fada847da",
        "market": "dummy_market_name",
        "direction": "buy",
        "created_at": "2017-11-26T10:11:12+00:00",
        "pair": "USD_BTC",
        "type": "limit",
        "quantity": "1",
        "rate": "8000",
        "id_on_market": "aaa-id-from-market",
        "status": "open",
        "closed_at": None,
        "canceled_at": None
    }]

    with open(file_name) as json_file:
        assert json.load(json_file) == expected

    exporter.import_from_file(file_name)

    os.remove(file_name)
