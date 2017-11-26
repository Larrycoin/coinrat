import datetime
from uuid import UUID

from decimal import Decimal

from coinrat.domain import Order, Pair, ORDER_TYPE_LIMIT


def test_order():
    order = Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
        'lorem_ipsum',
        datetime.datetime(2017, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        Pair('USD', 'BTC'),
        ORDER_TYPE_LIMIT,
        Decimal(2),
        Decimal(9000),
        'bbb-id-from-market',
        False,
        datetime.datetime(2017, 6, 7, 8, 9, 10, tzinfo=datetime.timezone.utc)
    )

    expected = 'Id: "16fd2706-8baf-433b-82eb-8c7fada847db, ' \
               + 'Market: "lorem_ipsum", ' \
               + 'Created: "2017-01-02T03:04:05+00:00, ' \
               + 'Open: "CLOSED, ' \
               + 'Closed: "2017-06-07T08:09:10+00:00, ' \
               + '"ID on market: "bbb-id-from-market", ' \
               + 'Pair: [USD-BTC], ' \
               + 'Type: "limit", ' \
               + 'Rate: 9000, ' \
               + 'Quantity: 2'

    assert expected == str(order)
