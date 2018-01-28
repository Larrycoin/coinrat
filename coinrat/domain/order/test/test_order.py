import copy
import datetime
from uuid import UUID

from decimal import Decimal

from coinrat.domain.pair import Pair
from coinrat.domain.order import Order, ORDER_TYPE_LIMIT, OrderMarketInfo, DIRECTION_BUY

DUMMY_ORDER_OPEN = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
    UUID('99fd2706-8baf-433b-82eb-8c7fada847da'),
    'lorem_ipsum',
    DIRECTION_BUY,
    datetime.datetime(2017, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
    Pair('USD', 'BTC'),
    ORDER_TYPE_LIMIT,
    Decimal('2'),
    Decimal('9000'),
    'bbb-id-from-market',
)


def test_open_order():
    order = DUMMY_ORDER_OPEN

    expected = 'BUY-OPEN, ' \
               + 'Id: "16fd2706-8baf-433b-82eb-8c7fada847db", ' \
               + 'Market: "lorem_ipsum", ' \
               + 'Created: "2017-01-02T03:04:05+00:00", ' \
               + 'Closed: "None", ' \
               + 'ID on market: "bbb-id-from-market", ' \
               + 'Pair: [USD_BTC], ' \
               + 'Type: "limit", ' \
               + 'Rate: "9000.00000000", ' \
               + 'Quantity: "2.00000000"'

    assert expected == str(order)
    assert order.is_open is True
    assert order.is_closed is False
    assert order.is_canceled is False


def test_closed_order():
    order: Order = copy.deepcopy(DUMMY_ORDER_OPEN)
    order.close(datetime.datetime(2017, 6, 7, 8, 9, 10, tzinfo=datetime.timezone.utc))

    assert order.is_open is False
    assert order.is_closed is True
    assert order.is_canceled is False
    assert order.closed_at.isoformat() == '2017-06-07T08:09:10+00:00'


def test_canceled_order():
    order: Order = copy.deepcopy(DUMMY_ORDER_OPEN)
    order.cancel(datetime.datetime(2018, 9, 6, 3, 1, 0, tzinfo=datetime.timezone.utc))

    assert order.is_open is False
    assert order.is_closed is False
    assert order.is_canceled is True
    assert order.canceled_at.isoformat() == '2018-09-06T03:01:00+00:00'


def test_order_info():
    order_info = OrderMarketInfo(DUMMY_ORDER_OPEN, True, None, Decimal('1'))

    assert DUMMY_ORDER_OPEN == order_info.order
    assert 'Order Id: "16fd2706-8baf-433b-82eb-8c7fada847db", OPEN, Closed at: "", Remaining quantity: "1"' \
           == str(order_info)
